from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy

from source.filesystem.IconManager import IconManager


class TabIcon(QPushButton):
    def __init__(self, parent, ext: str):
        super().__init__(parent)
        self.configurations()
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setIcon(IconManager.getInstance().getIcon(ext))
        self.setIconSize(QSize(16, 16))
        self.installEventFilter(self.parent())

    def configurations(self):
        self.setObjectName("TabIcon")
        self.setFixedSize(20, 40)
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

