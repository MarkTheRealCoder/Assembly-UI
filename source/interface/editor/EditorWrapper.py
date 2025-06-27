from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from source.asyncro import Scheduler
from source.comms import Database
from source.comms.events import ClosingEvent, NoTabEvent, ReadyEvent
from source.comms.handlers import EventRegister
from source.filesystem import HandleJson as HJ
from source.filesystem import HandleJson as HJ
from source.filesystem.documents import Document, FT
from source.filesystem.documents import Watcher
from source.interface.editor.Editor import Editor
from source.interface.editor.EditorFrame import EditorFrame
from source.interface.editor.me_system import TabManager, Tab
from source.interface.shared import createLayout


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
        self._frame = EditorFrame(self)

        layout.addWidget(self._tab_manager, 1)
        layout.addWidget(self._frame, 10)
        self.setLayout(layout)


class EditorWrapperLogic(EditorWrapperGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self._scheduler = None
        self._documents: dict[int: Document] = {}
        self.___consistency_checker = Watcher()

        self.setupConnections()

    def setupConnections(self):
        Database.OPEN_FILE.connect(self.openDocument)
        Database.ON_TAB_CLOSE.connect(self.closeTab)
        Database.ON_TAB_SELECTED.connect(self.setCurrentFile)
        Database.ON_TAB_SELECTED.connect(self.getFromDisk)

    def setCurrentFile(self):
        Database.CURRENT_FILE.setValue(
            self._documents.get(Database.ON_TAB_SELECTED.getValue(), None)
        )

    def openDocument(self, file: str):
        path = file if file is not None else Database.OPEN_FILE.getValue()
        if (paths := [d.getPath() for d in self._documents.values()]) and path in paths:
            return

        doc = Document(path)
        docHash = hash(doc)
        self._documents[docHash] = doc

        self.setupNewDocument(doc, docHash)
        self.initializeSchedulers(docHash)

    def setupNewDocument(self, doc: Document, docHash: int):
        self._tab_manager.addTab(
            docHash,
            self.document_uniqueness(doc),
            doc.getExtension()
        )
        self._frame.addEditor(docHash, Editor(self._frame), doc.text)

        Database.ON_TAB_SELECTED.setValue(docHash)
        Database.DOCTYPE.setValue(int(FT.findByExt(doc.getExtension())))

    def initializeSchedulers(self, docHash: int):
        if self._scheduler is None:
            self._scheduler = Scheduler(None, self.___auto_save)
            Database.DOCTYPE.setValue(int(FT.findByExt(
                self._documents[docHash].getExtension()
            )))
        self._frame.getEditor(docHash).textChanged.connect(
            self._scheduler.trigger
        )

    def document_uniqueness(self, document: Document):
        tabs = self.findChildren(Tab)
        name = str(document)
        unique = True
        for tab in tabs:
            text = tab.text()
            if text == name or name in text:
                unique = False
                tab.setText(
                    f"{self._documents[tab.getId()]:sub:{Database.FOLDER.getValue()}}"
                )
        if unique:
            return name
        return f"{document:sub:{Database.FOLDER.getValue()}}"

    def closeTab(self):
        docHash = Database.ON_TAB_CLOSE.getValue()
        self._documents.pop(docHash)
        if docHash == Database.ON_TAB_SELECTED.getValue():
            self._tab_manager.setActiveTab()
        self._frame.removeEditor(docHash)

    def getFromDisk(self):
        docHash = Database.ON_TAB_SELECTED.getValue()
        doc = self._documents.get(docHash)
        print(doc.getPath())
        if update := self.___consistency_checker.getDocumentUpdates(doc):
            editor = self._frame.getEditor(docHash)
            editor.setText(update)

    def ___auto_save(self):
        docHash = Database.ON_TAB_SELECTED.getValue()
        doc = self._documents.get(docHash)
        doc.text = self._frame.getEditorText(docHash)
        self.___consistency_checker.updateDocument(doc)

    @staticmethod
    def reset_variables():
        Database.ON_TAB_SELECTED.setValue(0)
        Database.CURRENT_FILE.setValue(None)
        Database.DOCTYPE.setValue(0)


@EventRegister.register(ClosingEvent, priority=EventRegister.URGENT)
@EventRegister.register(ReadyEvent, priority=EventRegister.HIGH)
class EditorWrapper(EditorWrapperLogic):
    def __init__(self, parent):
        super().__init__(parent)

    def onClosingEvent(self, e: ClosingEvent):
        if self._scheduler is not None:
            self._scheduler.terminate()
            del self._scheduler
        HJ.get_instance().set_files(
            list(map(lambda x: x.getPath(), self._documents.values()))
        )
        del self._documents

    def onReadyEvent(self, event):
        files = HJ.get_instance().get_files()
        if files:
            for f in files:
                self.openDocument(f)

    def eventFilter(self, obj, e: QEvent):
        if e.type() == NoTabEvent.gtype():
            EditorWrapper.reset_variables()
            return True
        return super().event(e)





















#
# @EventRegister.register(ClosingEvent, priority=EventRegister.URGENT)
# @EventRegister.register(ReadyEvent, priority=EventRegister.HIGH)
# class EditorWrapper(QFrame):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.___scheduler = None
#         self.___file_update = None
#
#         self._tab_manager: TabManager = None
#         self.___frame: EditorFrame = None
#
#         self.___documents: dict[int: Document] = {}
#
#         Database.OPEN_FILE.connect(self.openDocument)
#         Database.ON_TAB_CLOSE.connect(self.closeTab)
#
#         def set_current_file():
#             Database.CURRENT_FILE.setValue(self.___documents.get(Database.ON_TAB_SELECTED.getValue(), None))
#
#         Database.ON_TAB_SELECTED.connect(set_current_file)
#
#         self.configurations()
#
#     def configurations(self):
#         self.setObjectName("EditorWrapper")
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.setContentsMargins(0, 0, 0, 0)
#
#         layout: QVBoxLayout = createLayout(QVBoxLayout, self)
#         self._tab_manager = TabManager(self)
#         self.___frame = EditorFrame(self)
#
#         layout.addWidget(self._tab_manager, 1)
#         layout.addWidget(self.___frame, 10)
#         self.setLayout(layout)
#
#     def openDocument(self, file: str):
#         path = file if file is not None else Database.OPEN_FILE.getValue()
#         if (paths := [d.getPath() for d in self.___documents.values()]) and path in paths:
#             return
#         doc = Document(path)
#         docHash = hash(doc)
#
#         self.___documents[docHash] = doc
#
#         self._tab_manager.addTab(docHash, self.document_uniqueness(doc), doc.getExtension())
#         self.___frame.addEditor(docHash, Editor(self.___frame), doc.text)
#
#         Database.ON_TAB_SELECTED.setValue(docHash)
#         Database.DOCTYPE.setValue(int(FT.findByExt(doc.getExtension())))
#
#         if self.___file_update is None:
#             self.___file_update = Scheduler(None, self.___auto_save)
#
#         if self.___scheduler is None:
#             self.___scheduler = Scheduler(None, self.___auto_save)
#             Database.DOCTYPE.setValue(int(FT.findByExt(doc.getExtension())))
#         self.___frame.getEditor(docHash).textChanged.connect(self.___scheduler.trigger)
#
#     def document_uniqueness(self, document: Document):
#         tabs = self.findChildren(Tab)
#         name = str(document)
#         unique = True
#         for tab in tabs:
#             text = tab.text()
#             if text == name or name in text:
#                 unique = False
#                 tab.setText(f"{self.___documents[tab.getId()]:sub:{Database.FOLDER.getValue()}}")
#         if unique:
#             return name
#         return f"{document:sub:{Database.FOLDER.getValue()}}"
#
#     def closeTab(self):
#         docHash = Database.ON_TAB_CLOSE.getValue()
#         self.___documents.pop(docHash)
#         if docHash == Database.ON_TAB_SELECTED.getValue():
#             self._tab_manager.setActiveTab()
#         self.___frame.removeEditor(docHash)
#
#     def onClosingEvent(self, e: ClosingEvent):
#         if self.___scheduler is not None:
#             self.___scheduler.terminate()
#             del self.___scheduler
#         HJ.get_instance().set_files(list(map(lambda x: x.getPath(), self.___documents.values())))
#         del self.___documents
#
#     def ___auto_save(self):
#         docHash = Database.ON_TAB_SELECTED.getValue()
#         doc = self.___documents.get(docHash)
#         doc.text = self.___frame.getEditorText(docHash)
#
#     def ___get_from_disk(self):
#         docHash = Database.ON_TAB_SELECTED.getValue()
#         doc = self.___documents.get(docHash)
#         text = self.___frame.getEditorText(docHash)
#         if doc.text != text:
#             text = doc.text
#             editor = self.___frame.getEditor(docHash)
#             editor.setText(text)
#
#     def onReadyEvent(self, event):
#         files = HJ.get_instance().get_files()
#         if files:
#             for f in files:
#                 self.openDocument(f)
#
#     def eventFilter(self, obj, e: QEvent):
#         if e.type() == NoTabEvent.gtype():
#             EditorWrapper.reset_variables()
#             return True
#         return super().event(e)
#
#     @staticmethod
#     def reset_variables():
#         Database.ON_TAB_SELECTED.setValue(0)
#         Database.CURRENT_FILE.setValue(None)
#         Database.DOCTYPE.setValue(0)



