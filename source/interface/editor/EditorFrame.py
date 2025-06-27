from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QSizePolicy, QFrame

from source.comms import Database
from source.interface.editor.Editor import Editor
from source.interface.modals import DirectoryPicker
from source.interface.modals import FileCreator
from source.interface.modals import FilePicker
from source.interface.modals import modalOpen
from source.interface.shared import createLayout


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
            modalOpen(self, DirectoryPicker(), "Setup Working Directory")
        elif link == "open":
            modalOpen(self, FilePicker(), "Open a File")
        else:
            modalOpen(self, FileCreator(), "Create a New File")


class EditorFrameGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self._layout: QVBoxLayout = None
        self._editors: dict[int: Editor] = {
            0: DefaultFrame(self)
        }
        self._last_id = None

        self.configurations()
        self._layout.addWidget(self._editors.get(0), 1)

    def configurations(self):
        self.setObjectName("EditorFrame")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)

        self._layout = createLayout(QVBoxLayout, self)
        self.setLayout(self._layout)


class EditorFrameLogic(EditorFrameGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        Database.ON_TAB_SELECTED.connect(self.setActiveEditor)

    def addEditor(self, _id: int, editor: Editor, text: str):
        self._editors[_id] = editor
        editor.setText(text)

    def removeEditor(self, _id: int):
        self._editors.pop(_id)

    def getEditorText(self, _id: int):
        return self._editors.get(_id).text()

    def getEditor(self, _id: int):
        return self._editors.get(_id)

    def setActiveEditor(self, _id: int = None):
        _id = Database.ON_TAB_SELECTED.getValue()
        widget = self._editors.get(0)
        if self._last_id is not None:
            widget = self._editors.get(self._last_id)
        widget.hide()
        new_widget = self._editors.get(_id)
        self._layout.replaceWidget(widget, new_widget)
        self._last_id = _id
        new_widget.show()
        self.update()


class EditorFrame(EditorFrameLogic):
    def __init__(self, parent):
        super().__init__(parent)


# class EditorFrame(QFrame):
#     def __init__(self, parent):
#         super().__init__(parent)
#         self.___layout: QVBoxLayout = None
#         self.___editors: dict[int: Editor] = {
#             0: DefaultFrame(self)
#         }
#         self.___last_id = None
#
#         Database.ON_TAB_SELECTED.connect(self.setActiveEditor)
#
#         self.configurations()
#
#         self.___layout.addWidget(self.___editors.get(0), 1)
#
#     def configurations(self):
#         self.setObjectName("EditorFrame")
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.setContentsMargins(0, 0, 0, 0)
#
#         self.___layout = createLayout(QVBoxLayout, self)
#         self.setLayout(self.___layout)
#
#     def addEditor(self, _id: int, editor: Editor, text: str):
#         self.___editors[_id] = editor
#         editor.setText(text)
#
#     def removeEditor(self, _id: int):
#         self.___editors.pop(_id)
#
#     def getEditorText(self, _id: int):
#         return self.___editors.get(_id).text()
#
#     def getEditor(self, _id: int):
#         return self.___editors.get(_id)
#
#     def setActiveEditor(self, _id: int = None):
#         _id = Database.ON_TAB_SELECTED.getValue()
#         widget = self.___editors.get(0)
#         if self.___last_id is not None:
#             widget = self.___editors.get(self.___last_id)
#         widget.hide()
#         new_widget = self.___editors.get(_id)
#         self.___layout.replaceWidget(widget, new_widget)
#         self.___last_id = _id
#         new_widget.show()
#         self.update()
