from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QSizePolicy, QFrame

from src.interface.commons.Commons import createLayout
from src.interface.components.codespace.Editor import Editor
from src.interface.external.ToolWindow import wOpen
from src.interface.external.filemanager.DirectoryPicker import DirectoryPicker
from src.interface.external.filemanager.FileCreator import FileCreator
from src.interface.external.filemanager.FilePicker import FilePicker
from src.signals.Variables import DataBase


class DefaultFrame(QLabel):
    def __init__(self, parent):
        super().__init__(parent)

        self.configurations()
        self.setText("""
        <a href="cwd" style="color: #A4FFFC;">Setup</a> the working directory.<br><br>
        <a href="new" style="color: #A4FFFC;">Create</a> a new file.<br><br>
        <a href="open" style="color: #A4FFFC;">Open</a> a file.
        """)
        self.linkActivated.connect(self.linkHandler)

    def configurations(self):
        self.setTextFormat(Qt.RichText)
        self.setAlignment(Qt.AlignCenter)

    def linkHandler(self, link: str):
        if link == "cwd":
            wOpen(self, DirectoryPicker(), "Setup Working Directory")
        elif link == "open":
            wOpen(self, FilePicker(), "Open a File")
        else:
            wOpen(self, FileCreator(), "Create a New File")


class EditorFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.___layout: QVBoxLayout = None
        self.___editors: dict[int: Editor] = {
            0: DefaultFrame(self)
        }
        self.___last_id = None

        DataBase.ON_TAB_SELECTED.connect(self.setActiveEditor)

        self.configurations()

        self.___layout.addWidget(self.___editors.get(0), 1)

    def configurations(self):
        self.setObjectName("EditorFrame")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self.___layout = createLayout(QVBoxLayout, self)
        self.setLayout(self.___layout)

    def addEditor(self, _id: int, editor: Editor, text: str):
        self.___editors[_id] = editor
        editor.setText(text)

    def removeEditor(self, _id: int):
        self.___editors.pop(_id)

    def getEditorText(self, _id: int):
        return self.___editors.get(_id).text()

    def getEditor(self, _id: int):
        return self.___editors.get(_id)

    def setActiveEditor(self, _id: int = None):
        _id = DataBase.ON_TAB_SELECTED.getValue()
        widget = self.___editors.get(0)
        if self.___last_id is not None:
            widget = self.___editors.get(self.___last_id)
        widget.hide()
        new_widget = self.___editors.get(_id)
        self.___layout.replaceWidget(widget, new_widget)
        self.___last_id = _id
        new_widget.show()
        self.update()
