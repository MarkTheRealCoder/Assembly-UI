from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy

from source.filesystem import find_path
from source.interface.templates import GenericButton


class MinimizeButton(GenericButton):
    def __init__(self, parent, properties: dict[str, bool] = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.setIcon(self.rerenderIcon(QIcon(find_path("minimize.svg")), "#569CD6"))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Minimize")

        self.clicked.connect(self.on_press)

    def on_press(self):
        self.window().showMinimized()