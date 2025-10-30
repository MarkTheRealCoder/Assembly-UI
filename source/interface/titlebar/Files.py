from PyQt5.QtWidgets import QMenu

from source.interface.modals import modalOpen, FilePicker, DirectoryPicker, FileCreator, FileSaver, SettingsWidget
from source.interface.templates import GenericButton
from source.platform import Desktop


class FileMenu(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
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
        menu.addAction("Change Working Path", lambda: modalOpen(self.parent().mw, DirectoryPicker(), "Setup Working Directory"))
        menu.addSeparator()
        menu.addAction("Open", lambda: modalOpen(self.parent().mw, FilePicker(), "Open a File"))
        menu.addAction("New", lambda: modalOpen(self.parent().mw, FileCreator(), "Create a New File"))
        menu.addAction("Save as...", lambda: modalOpen(self.parent().mw, FileSaver(), "Save the current file as ..."))
        menu.addSeparator()
        menu.addAction("Settings", lambda: modalOpen(self.parent().mw, SettingsWidget(self.parent().mw), "Settings"))
        self.setMenu(menu)
