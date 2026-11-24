import logging
import threading
from pathlib import Path

from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from source.asyncro import Scheduler
from source.comms import Database
from source.comms.events import ClosingEvent, NoTabEvent, ReadyEvent, RunEvent, TabAddedEvent, FindShortcutEvent
from source.comms.handlers import EventRegister
from source.filesystem.documents import Document
from source.filesystem.documents import Watcher
from source.interface.editor.Editor import Editor
from source.interface.editor.EditorFrame import EditorFrame
from source.interface.editor.me_system import TabManager, Tab
from source.interface.shared import createLayout, Settings
from source.interface.templates import FindWidget


class EditorWrapperGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._tab_manager: TabManager = None
        self._frame: EditorFrame = None
        self.configurations()

    def configurations(self):
        self.setObjectName("EditorWrapper")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        self._tab_manager = TabManager(self)
        self._find_widget = FindWidget(self, "editor")
        self._frame = EditorFrame(self)

        layout.addWidget(self._tab_manager, 1)
        layout.addWidget(self._find_widget, 1)
        layout.addWidget(self._frame, 10)
        self.setLayout(layout)


class EditorWrapperLogic(EditorWrapperGraphics):
    """ Keeps open documents, their tabs and their editors in sync, and autosaves edits """

    def __init__(self, parent):
        super().__init__(parent)
        self._scheduler = None
        self._documents: dict[int: Document] = {}
        self._closed = False
        self.___consistency_checker = Watcher()
        self.___pending_saves: dict[int, str] = {}
        self.___pending_lock = threading.Lock()
        self.___save_lock = threading.Lock()

        self.setupConnections()

    def setupConnections(self):
        Settings.addNotificationGroup("editor/current", self.openDocument)
        Database.ON_FILE_REPLACED.connect(self.reloadReplacedFile)
        Database.ON_EXECUTION_LINE.connect(self.showExecutionLine)
        Database.ON_TAB_CLOSE.connect(self.closeTab)
        Database.ON_TAB_SELECTED.connect(self.setCurrentFile)
        Database.ON_TAB_SELECTED.connect(self.getFromDisk)
        Database.ON_TAB_SELECTED.connect(self._find_widget.sync)
        Database.ON_TAB_SELECTED.connect(lambda: EventRegister.send(FindShortcutEvent(True), "editor") if Database.ON_TAB_SELECTED.getValue() == 0 else None)

    def setCurrentFile(self):
        _id = Database.ON_TAB_SELECTED.getValue()
        if doc := self._documents.get(_id, None):
            Settings.set("editor/current", str(doc))
        else:
            Settings.remove("editor/current")

    def openDocument(self, file: str = None):
        """ Open a file in a new tab, or select its tab if it is already open """
        path = Settings.get("editor/current", None) if file is None else file

        for docHash, document in self._documents.items():
            if document.getPath() == path:
                if Database.ON_TAB_SELECTED.getValue() != docHash:
                    self._tab_manager.setActiveTab(docHash)
                return

        doc = Document(path)
        docHash = hash(doc)
        self._documents[docHash] = doc

        self.setupNewDocument(doc, docHash)
        self.initializeSchedulers(docHash)

    def showExecutionLine(self):
        """
        Highlight the next line of the running program in the editor of its file.
        The editor scrolls to the line only if that file is in the selected tab.
        """
        path, line = Database.ON_EXECUTION_LINE.getValue()
        selected = Database.ON_TAB_SELECTED.getValue()
        for docHash, document in self._documents.items():
            editor = self._frame.getEditor(docHash)
            if editor is None:
                continue
            if document.getPath() == path:
                editor.setExecutionLine(line, follow=docHash == selected)
            else:
                editor.setExecutionLine(-1)

    def reloadReplacedFile(self, path: str):
        """ Reload the open tabs of a file that was replaced on disk """
        destination = Path(path)
        for docHash, document in list(self._documents.items()):
            try:
                if not destination.samefile(document.getPath()):
                    continue
                # A queued save holds the old text and must not overwrite the new file.
                with self.___save_lock:
                    with self.___pending_lock:
                        self.___pending_saves.pop(docHash, None)
                    document.reload()
                    self.___consistency_checker.updateDocument(document)
            except (OSError, UnicodeError) as error:
                logging.getLogger(__name__).warning("Could not reload %s: %s", document, error)
                continue
            self._frame.getEditor(docHash).setText(document.text)

    def setupNewDocument(self, doc: Document, docHash: int):
        self._tab_manager.addTab(
            docHash,
            self.document_uniqueness(doc),
            doc.getExtension()
        )
        self._frame.addEditor(docHash, Editor(self._frame, doc.getExtension(), docHash), doc.text)

        Database.ON_TAB_SELECTED.setValue(docHash)
        EventRegister.send(TabAddedEvent(), "Tab")

    def initializeSchedulers(self, docHash: int):
        if self._scheduler is None:
            self._scheduler = Scheduler(None, self._savePending)
        self._frame.getEditor(docHash).textChanged.connect(
            lambda: self.___queue_save(docHash)
        )

    def document_uniqueness(self, document: Document):
        """ Return the tab name: the file name, or its path from the working directory when names clash """
        tabs = self.findChildren(Tab)
        name = repr(document)
        unique = True
        for tab in tabs:
            text = tab.text()
            if text == name or name in text:
                unique = False
                tab.setText(
                    f"{self._documents[tab.getId()]:sub:{Settings.get('application/cwd')}}"
                )
        if unique:
            return name
        return f"{document:sub:{Settings.get('application/cwd')}}"

    def closeTab(self):
        docHash = Database.ON_TAB_CLOSE.getValue()
        self._savePending()
        self._documents.pop(docHash)
        if docHash == Database.ON_TAB_SELECTED.getValue():
            self._tab_manager.setActiveTab()
        self._frame.removeEditor(docHash)

    def getFromDisk(self):
        """ Show in the selected editor the changes made to its file outside the app """
        docHash = Database.ON_TAB_SELECTED.getValue()
        doc = self._documents.get(docHash)
        if doc is None:
            return
        self._savePending()
        if update := self.___consistency_checker.getDocumentUpdates(doc):
            editor = self._frame.getEditor(docHash)
            editor.setText(update)

    def ___queue_save(self, docHash: int):
        # Qt widgets are read here, on the GUI thread. The scheduler thread only writes files.
        if docHash not in self._documents:
            return
        text = self._frame.getEditorText(docHash)
        with self.___pending_lock:
            self.___pending_saves[docHash] = text
        if self._scheduler is not None:
            self._scheduler.trigger()

    def _savePending(self):
        """ Write the queued edits to disk, queueing again the ones that fail """
        with self.___save_lock:
            with self.___pending_lock:
                pending, self.___pending_saves = self.___pending_saves, {}
            for docHash, text in pending.items():
                doc = self._documents.get(docHash)
                if doc is None:
                    continue
                try:
                    doc.text = text
                    self.___consistency_checker.updateDocument(doc)
                except (OSError, UnicodeError) as error:
                    logging.getLogger(__name__).warning("Could not save %s: %s", doc, error)
                    with self.___pending_lock:
                        self.___pending_saves.setdefault(docHash, text)

    @staticmethod
    def reset_variables():
        Database.ON_TAB_SELECTED.setValue(0)
        Settings.remove("editor/current")


@EventRegister.register(RunEvent, "Editor", priority=EventRegister.URGENT)
@EventRegister.register(FindShortcutEvent, "editor", priority=EventRegister.URGENT)
@EventRegister.register(ClosingEvent, priority=EventRegister.URGENT)
@EventRegister.register(ReadyEvent, priority=EventRegister.HIGH)
class EditorWrapper(EditorWrapperLogic):
    """ Editor area with the tab bar, the find widget and the editors """

    def __init__(self, parent):
        super().__init__(parent)

    def onRunEvent(self, event: RunEvent):
        """ Write pending edits to disk before the interpreter reads the file """
        self._savePending()
        event.accept()

    def onFindShortcutEvent(self, event: FindShortcutEvent):
        """ Show or hide the find widget while a file is open """
        if self._frame.getEditor(Database.ON_TAB_SELECTED.getValue()) is not None:
            if event.mustClose():
                self._find_widget.toggle(True)
                return
            self._find_widget.toggle()

    def onClosingEvent(self, e: ClosingEvent):
        """ Stop autosave, flush pending edits and store the open files """
        # The close button and QApplication.aboutToQuit can both send this event.
        if self._closed:
            e.accept()
            return
        self._closed = True
        if self._scheduler is not None:
            self._scheduler.terminate()
            self._scheduler = None
        self._savePending()
        Settings.silentSet("editor/files", list(map(lambda x: str(x), self._documents.values())))
        self._documents = {}
        e.accept()

    def onReadyEvent(self, event):
        """ Reopen the files stored at the last closing """
        files = Settings.get("editor/files", [], list)
        if files:
            for f in files:
                self.openDocument(f)
        event.accept()

    def eventFilter(self, obj, e: QEvent):
        if e.type() == NoTabEvent.gtype():
            EditorWrapper.reset_variables()
            return True
        return super().event(e)
