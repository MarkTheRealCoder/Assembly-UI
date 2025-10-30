from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QMainWindow

from source.filesystem import find_path
from source.interface.templates import GenericButton


class MinimizeButton(GenericButton):
    def __init__(self, parent, mw: QMainWindow):
        super().__init__(parent)
        self.mainwindow = mw
        self.setIcon(self.rerenderIcon(QIcon(find_path("minimize.svg")), "#569CD6"))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Minimize")

    def mousePressEvent(self, e: QMouseEvent):
        self.mainwindow.showMinimized()
        e.accept()