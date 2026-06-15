from PyQt5.QtWidgets import QMenu, QSizePolicy

from source.filesystem import find_path
from source.interface.modals import createSubWindow, Renderer
from source.interface.templates import GenericButton
from source.platform import Desktop


class HelpMenu(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.setText("Help")
        self.setObjectName("Help")
        self.setupFontAndAlignment()
        menu = self.help_menu(self)
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
    def help_menu(hndl):
        menu = QMenu(hndl)
        menu.addAction("Features", lambda: createSubWindow("Features", hndl.window(), Renderer, find_path("features.html")))
        menu.addSeparator()
        menu.addAction("8088 Instructions", lambda: createSubWindow("8088", hndl.window(), Renderer, find_path("8088.html")))
        menu.addAction("IJVM Instructions", lambda: createSubWindow("IJVM", hndl.window(), Renderer, find_path("IJVM.html")))
        return menu
