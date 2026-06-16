from PyQt5.QtWidgets import QMenu, QSizePolicy

from source.interface.modals.filemanager import pick_file, pick_new_file, pick_working_directory, save_file_as
from source.interface.templates import GenericButton, toast_safe_exec
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
        menu.addAction("Change Working Path", toast_safe_exec(hndl.window(), lambda: pick_working_directory(hndl.window())))
        menu.addSeparator()
        menu.addAction("Open",
                    toast_safe_exec(
                        hndl.window(),
                        lambda: pick_file(hndl.window())
                        )
                    )
        menu.addAction("New", toast_safe_exec(hndl.window(), lambda: pick_new_file(hndl.window())))
        menu.addAction("Save as...", toast_safe_exec(hndl.window(), lambda: save_file_as(hndl.window())))
        return menu
