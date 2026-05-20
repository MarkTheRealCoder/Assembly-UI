from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QSizePolicy

from source.filesystem import find_path
from source.interface.shared import Settings
from source.interface.templates import GenericButton


class MaximizeButton(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.maximize_icon = self.rerenderIcon(QIcon(find_path("maximize.svg")), "#569CD6")
        self.restore_icon = self.rerenderIcon(QIcon(find_path("restore.svg")), "#569CD6")

        self.setIcon(self.maximize_icon)
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Maximize")

        Settings.addNotificationGroup("mainwindow/fullscreen", self.updateIcon)

    def updateIcon(self):
        if Settings.get("mainwindow/fullscreen", False, bool):
            self.setIcon(self.restore_icon)
        else:
            self.setIcon(self.maximize_icon)

    def mousePressEvent(self, e: QMouseEvent):
        w = self.window()
        if not w.isMaximized():
            w.showMaximized()
            Settings.set("mainwindow/fullscreen", True)
        else:
            w.showNormal()
            Settings.set("mainwindow/fullscreen", False)
        e.accept()