from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy

from source.filesystem import find_path
from source.interface.shared import Settings
from source.interface.templates import GenericButton


class MaximizeButton(GenericButton):
    def __init__(self, parent, properties: dict[str, bool] = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.maximize_icon = self.rerenderIcon(QIcon(find_path("maximize.svg")), "#569CD6")
        self.restore_icon = self.rerenderIcon(QIcon(find_path("restore.svg")), "#569CD6")
        self.window().MAXBUTTON_RECT = lambda: self.get_rect()

        self.setIcon(self.maximize_icon)
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Maximize")

        Settings.addNotificationGroup("mainwindow/fullscreen", self.updateIcon)

        self.clicked.connect(self.on_press)

    def updateIcon(self):
        if Settings.get("mainwindow/fullscreen", False, bool):
            self.setIcon(self.restore_icon)
        else:
            self.setIcon(self.maximize_icon)

    def get_rect(self) -> tuple[int, int, int, int]:
        pos = self.mapTo(self.window(), self.rect().topLeft())
        return pos.x(), pos.y(), self.width(), self.height()

    def on_press(self):
        w = self.window()
        if not w.isMaximized():
            w.showMaximized()
            Settings.set("mainwindow/fullscreen", True)
        else:
            w.showNormal()
            Settings.set("mainwindow/fullscreen", False)