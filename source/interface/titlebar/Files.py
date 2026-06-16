from PyQt5.QtWidgets import QMenu, QSizePolicy

from source.interface.modals import modalOpen, FilePicker, DirectoryPicker, FileCreator, FileSaver
from source.interface.templates import GenericButton, create_toast, toast_safe_exec
from source.platform import Desktop


class FileMenu(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.setText("File")
        self.setObjectName("File")
        self.setupFontAndAlignment()
        menu = self.file_menu(self)
        menu.aboutToShow.connect(lambda: self.menuOpen())
        menu.aboutToHide.connect(lambda: self.menuClose())
        self.setMenu(menu)

    def setupFontAndAlignment(self):
        # Set scalable font
        font = Desktop.createScalableFont("Anonymous Pro", 12, False)
        self.setFont(font)

    def menuOpen(self):
        self.setProperty("menuOpen", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def menuClose(self):
        self.setProperty("menuOpen", False)
        self.style().unpolish(self)
        self.style().polish(self)

    @staticmethod
    def file_menu(hndl):
        menu = QMenu(hndl)
        menu.addAction("Change Working Path", toast_safe_exec(hndl.window(), lambda: modalOpen(hndl.window(), DirectoryPicker(), "Setup Working Directory")))
        menu.addSeparator()
        menu.addAction("Open",
                    toast_safe_exec(
                        hndl.window(),
                        lambda: modalOpen(hndl.window(), FilePicker(), "Open a File")
                        )
                    )
        menu.addAction("New", toast_safe_exec(hndl.window(), lambda: modalOpen(hndl.window(), FileCreator(), "Create a New File")))
        menu.addAction("Save as...", toast_safe_exec(hndl.window(), lambda: FileMenu._filesaver(hndl.window())))
        return menu

    @staticmethod
    def _filesaver(window):
        fs = FileSaver()
        if fs is None:
            create_toast(window, "There is no file to save!", "error")
            return
        modalOpen(window, fs, "Save the current file as ...")
