from PyQt5.QtWidgets import QTabWidget, QSizePolicy, QWidget

from src.graphics.components.editorcomponents.Editor import Editor
from src.tools.Variables import DataBase as db


class TabEditorWrapper(QTabWidget):
    def __init__(self, parent: QWidget):
        super().__init__(parent)
        self.setObjectName("EditorTabManager")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        db.OPEN_FILE.connect(self.addTabDynamically)

    def addTabDynamically(self):
        e = Editor(self)
        e.setText("Hello")
        self.addTab(e, db.OPEN_FILE.getValue())
