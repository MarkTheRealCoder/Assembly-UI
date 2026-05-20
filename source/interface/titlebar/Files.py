from PyQt5.QtWidgets import QMenu, QSizePolicy

from source.interface.modals import modalOpen, FilePicker, DirectoryPicker, FileCreator, FileSaver
from source.interface.templates import GenericButton
from source.platform import Desktop


class FileMenu(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.setText("File")
        self.setObjectName("File")
        self.setupFontAndAlignment()
        self.configure()

    def setupFontAndAlignment(self):
        # Set scalable font
        font = Desktop.createScalableFont("Anonymous Pro", 12, False)
        self.setFont(font)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Change Working Path", lambda: modalOpen(self.window(), DirectoryPicker(), "Setup Working Directory"))
        menu.addSeparator()
        menu.addAction("Open", lambda: modalOpen(self.window(), FilePicker(), "Open a File"))
        menu.addAction("New", lambda: modalOpen(self.window(), FileCreator(), "Create a New File"))
        menu.addAction("Save as...", lambda: modalOpen(self.window(), FileSaver(), "Save the current file as ..."))
        self.setMenu(menu)
