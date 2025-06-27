from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QMainWindow

from source.filesystem import find_path
from source.interface.templates import GenericButton


class MaximizeButton(GenericButton):
    def __init__(self, parent, mw: QMainWindow):
        super().__init__(parent)
        self.mainwindow = mw
        self.setIcon(QIcon(find_path("maximize.png")))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Minimize")

    def mousePressEvent(self, e: QMouseEvent):
        if not self.isTriggerable():
            e.ignore()
            return
        if not self.mainwindow.isMaximized():
            self.mainwindow.showMaximized()
            self.setIcon(QIcon(find_path("restore.png")))
        else:
            self.mainwindow.showNormal()
            self.setIcon(QIcon(find_path("maximize.png")))