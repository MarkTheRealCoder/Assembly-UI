from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon, QMouseEvent
from PyQt5.QtWidgets import QSizePolicy

from source.filesystem import find_path
from source.interface.templates import GenericButton


class IconButton(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        icon_size: QSize = QSize()
        size = 20
        icon_size.setHeight(size)
        icon_size.setWidth(size)
        icon = QIcon(find_path("Logo.png"))
        self.setIcon(icon)
        self.setIconSize(icon_size)
        self.setObjectName("Icon")
        self.setFixedSize(size+15, size+14)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def mousePressEvent(self, e: QMouseEvent):
        if not self.isTriggerable():
            e.ignore()
            return
        super().mousePressEvent(e)