from PyQt5.QtGui import QMouseEvent
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QMenu, QWidget

from source.filesystem import find_path
from source.interface.modals import createSubWindow, Renderer
from source.interface.templates import GenericButton


class HelpMenu(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setText(" Help")
        self.setObjectName("Help")
        self.configure()

    def mousePressEvent(self, e: QMouseEvent):
        if not self.isTriggerable():
            e.ignore()
            return
        super().mousePressEvent(e)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Features", lambda: createSubWindow("Features", self, QWidget))
        menu.addSeparator()
        menu.addAction("8088 Instructions", lambda: createSubWindow("8088", self, Renderer, find_path("8088.html")))
        menu.addAction("IJVM Instructions", lambda: createSubWindow("IJVM", self, Renderer, find_path("IJVM.html")))
        self.setMenu(menu)