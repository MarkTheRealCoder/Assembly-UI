from PyQt5.QtWidgets import QMenu

from source.filesystem import find_path
from source.interface.modals import createSubWindow, Renderer
from source.interface.templates import GenericButton
from source.platform import Desktop


class HelpMenu(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText("Help")
        self.setObjectName("Help")
        self.setupFontAndAlignment()
        self.configure()

    def setupFontAndAlignment(self):
        # Set scalable font
        font = Desktop.createScalableFont("Anonymous Pro", 12, False)
        self.setFont(font)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Features", lambda: createSubWindow("Features", self, Renderer, find_path("features.html")))
        menu.addSeparator()
        menu.addAction("8088 Instructions", lambda: createSubWindow("8088", self, Renderer, find_path("8088.html")))
        menu.addAction("IJVM Instructions", lambda: createSubWindow("IJVM", self, Renderer, find_path("IJVM.html")))
        self.setMenu(menu)
