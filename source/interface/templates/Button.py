from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QSizePolicy


class GenericButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

