from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMenu

from source.interface.modals import modalOpen, FilePicker, DirectoryPicker, FileCreator, FileSaver
from source.interface.templates import GenericButton


class FileMenu(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText(" File")
        self.setObjectName("File")
        self.configure()

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Change Working Path", lambda: modalOpen(self.parent().mw, DirectoryPicker(), "Setup Working Directory"))
        menu.addSeparator()
        menu.addAction("Open", lambda: modalOpen(self.parent().mw, FilePicker(), "Open a File"))
        menu.addAction("New", lambda: modalOpen(self.parent().mw, FileCreator(), "Create a New File"))
        menu.addAction("Save as...", lambda: modalOpen(self.parent().mw, FileSaver(), "Save the current file as ..."))
        menu.addSeparator()
        menu.addAction("Options")
        self.setMenu(menu)

    def mousePressEvent(self, e: QMouseEvent):
        if not self.isTriggerable():
            e.ignore()
            return
        super().mousePressEvent(e)