from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QTabWidget, QSizePolicy, QWidget

from src.graphics.components.editor.Editor import Editor
from src.graphics.components.editor.editorwrapper.wrapperbar.TabManager import TabManager
from src.tools.DataManager import HandleJson as HJ
from src.tools.Scheduler import Scheduler
from src.tools.Variables import DataBase as db
from src.tools.documents.Document import Document
from src.tools.documents.FileTypes import FT


class TabEditorWrapper(QTabWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.configurations()

        self.___documents: dict[int: Document] = {}

        self.___index = -1
        self.___scheduler: Scheduler = None

        db.OPEN_FILE.connect(self.addTabDynamically)
        db.ON_MAIN_WINDOW_LOAD.connect(self.___restore)

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.currentChanged.connect(self.change_document)
        self.tabCloseRequested.connect(self.closeTab)
        db.CLOSING_MAIN_WINDOW.connect(self.___emergency)

        self.setTabBar(TabManager(self))

    def addTabDynamically(self, file: str = None):
        path = file if file is not None else db.OPEN_FILE.getValue()
        if (paths := [d.getPath() for d in self.___documents.values()]) and path in paths:
            return
        doc = Document(path)
        docHash = hash(doc)
        e = Editor(self)
        e.setText(doc.text)

        index = self.addTab(e, self.document_uniqueness(doc))
        self.tabBar().setTabData(index, docHash)
        self.___documents[docHash] = doc
        if self.___scheduler is None:
            self.___scheduler = Scheduler(None, self.___auto_save)
            db.DOCTYPE.setValue(int(FT.findByExt(doc.getExtension())))
        e.textChanged.connect(self.___scheduler.trigger)

    def document_uniqueness(self, document: Document):
        tabBar = self.tabBar()
        tabs = {index: [tabBar.tabData(index), tabBar.tabText(index)] for index in range(self.count())}
        name = str(document)
        index = -1
        for indx, info in tabs.items():
            if info[1] == name:
                index = indx
                break
        if index == -1:
            return name
        self.setTabText(index, f"{self.___documents[tabs[index][0]]:sub:{db.FOLDER.getValue()}}")
        return f"{document:sub:{db.FOLDER.getValue()}}"

    def change_document(self, index: int):
        self.___index = index
        if self.___scheduler is not None:
            if index == -1:
                self.___scheduler.terminate()
                del self.___scheduler
                self.___scheduler = None
            else:
                docHash = self.tabBar().tabData(index)
                db.DOCTYPE.setValue(int(FT.findByExt(self.___documents.get(docHash).getExtension())))

    def closeTab(self, index: int):
        docHash = self.tabBar().tabData(index)
        self.___documents.pop(docHash)
        self.removeTab(index)

    def ___emergency(self):
        if self.___scheduler is not None:
            self.___scheduler.terminate()
            del self.___scheduler
        HJ.get_instance().set_files(list(map(lambda x: x.getPath(), self.___documents.values())))
        del self.___documents

    def ___auto_save(self):
        docHash = self.tabBar().tabData(self.___index)
        doc: Document = self.___documents.get(docHash)
        e: Editor = self.widget(self.___index) # noqas
        doc.text = e.text()

    def ___restore(self):
        files = HJ.get_instance().get_files()
        if files:
            for f in files:
                self.addTabDynamically(f)

