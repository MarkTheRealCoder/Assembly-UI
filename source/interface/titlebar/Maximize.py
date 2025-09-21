from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QMainWindow

from source.filesystem import find_path
from source.interface.shared import Settings
from source.interface.templates import GenericButton


class MaximizeButton(GenericButton):
    def __init__(self, parent, mw: QMainWindow):
        super().__init__(parent)
        self.mainwindow = mw
        self.setIcon(QIcon(find_path("maximize.png")))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Maximize")
        Settings.addNotificationGroup("mainwindow/fullscreen", self.updateIcon)

    def updateIcon(self):
        if Settings.get("mainwindow/fullscreen", False, bool):
            self.setIcon(QIcon(find_path("restore.png")))
        else:
            self.setIcon(QIcon(find_path("maximize.png")))

    def mousePressEvent(self, e: QMouseEvent):
        if not self.mainwindow.isMaximized():
            self.mainwindow.showMaximized()
            Settings.set("mainwindow/fullscreen", True)
        else:
            self.mainwindow.showNormal()
            Settings.set("mainwindow/fullscreen", False)
        e.accept()