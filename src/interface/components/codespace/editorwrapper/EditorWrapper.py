from PyQt5.QtCore import QEvent
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from src.asynctasks.Scheduler import Scheduler
from src.eventhandlers.Register import EventRegister
from src.events.data.ClosingEvent import ClosingEvent
from src.events.data.NoTabEvent import NoTabEvent
from src.events.data.ReadyEvent import ReadyEvent
from src.filesystem.DataManager import HandleJson as HJ
from src.filesystem.documents.Document import Document
from src.filesystem.documents.FileTypes import FT
from src.interface.commons.Commons import createLayout
from src.interface.components.codespace.Editor import Editor
from src.interface.components.codespace.editorwrapper.support.EditorFrame import EditorFrame
from src.interface.components.codespace.editorwrapper.support.tabmanager.TabManager import TabManager
from src.interface.components.codespace.editorwrapper.support.tabmanager.tab.Tab import Tab
from src.signals.Variables import DataBase as db, DataBase


@EventRegister.register(ClosingEvent, priority=EventRegister.URGENT)
@EventRegister.register(ReadyEvent, priority=EventRegister.HIGH)
class EditorWrapper(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.___scheduler = None
        self.___tab_manager: TabManager = None
        self.___frame: EditorFrame = None

        self.___documents: dict[int: Document] = {}

        DataBase.OPEN_FILE.connect(self.openDocument)
        DataBase.ON_TAB_CLOSE.connect(self.closeTab)

        def set_current_file():
            DataBase.CURRENT_FILE.setValue(self.___documents.get(DataBase.ON_TAB_SELECTED.getValue(), None))

        DataBase.ON_TAB_SELECTED.connect(set_current_file)

        self.configurations()

    def configurations(self):
        self.setObjectName("EditorWrapper")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        self.___tab_manager = TabManager(self)
        self.___frame = EditorFrame(self)

        layout.addWidget(self.___tab_manager, 1)
        layout.addWidget(self.___frame, 10)
        self.setLayout(layout)

    def openDocument(self, file: str):
        path = file if file is not None else db.OPEN_FILE.getValue()
        if (paths := [d.getPath() for d in self.___documents.values()]) and path in paths:
            return
        doc = Document(path)
        docHash = hash(doc)

        self.___documents[docHash] = doc

        self.___tab_manager.addTab(docHash, self.document_uniqueness(doc), doc.getExtension())
        self.___frame.addEditor(docHash, Editor(self.___frame), doc.text)

        DataBase.ON_TAB_SELECTED.setValue(docHash)
        DataBase.DOCTYPE.setValue(int(FT.findByExt(doc.getExtension())))

        if self.___scheduler is None:
            self.___scheduler = Scheduler(None, self.___auto_save)
            db.DOCTYPE.setValue(int(FT.findByExt(doc.getExtension())))
        self.___frame.getEditor(docHash).textChanged.connect(self.___scheduler.trigger)

    def document_uniqueness(self, document: Document):
        tabs = self.findChildren(Tab)
        name = str(document)
        unique = True
        for tab in tabs:
            text = tab.text()
            if text == name or name in text:
                unique = False
                tab.setText(f"{self.___documents[tab.getId()]:sub:{db.FOLDER.getValue()}}")
        if unique:
            return name
        return f"{document:sub:{db.FOLDER.getValue()}}"

    def closeTab(self):
        docHash = DataBase.ON_TAB_CLOSE.getValue()
        self.___documents.pop(docHash)
        if docHash == DataBase.ON_TAB_SELECTED.getValue():
            self.___tab_manager.setActiveTab()
        self.___frame.removeEditor(docHash)

    def onClosingEvent(self, e: ClosingEvent):
        if self.___scheduler is not None:
            self.___scheduler.terminate()
            del self.___scheduler
        HJ.get_instance().set_files(list(map(lambda x: x.getPath(), self.___documents.values())))
        del self.___documents

    def ___auto_save(self):
        docHash = DataBase.ON_TAB_SELECTED.getValue()
        doc = self.___documents.get(docHash)
        doc.text = self.___frame.getEditorText(docHash)

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

    @staticmethod
    def reset_variables():
        DataBase.ON_TAB_SELECTED.setValue(0)
        DataBase.CURRENT_FILE.setValue(None)
        DataBase.DOCTYPE.setValue(0)
