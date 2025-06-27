from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton


class Icon(QPushButton):
    def __init__(self, parent, icon: QIcon):
        super().__init__(parent)
        self.configurations(icon)

    def configurations(self, icon: QIcon):
        self.setObjectName("TabIcon")
        self.setFixedSize(20, 25)
        self.setIcon(icon)
        self.setIconSize(QSize(16, 16))
        self.setContentsMargins(0, 0, 0, 0)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def mousePressEvent(self, e):
        self.parent().mousePressEvent(e)
