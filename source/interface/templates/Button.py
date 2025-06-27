from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QPushButton, QSizePolicy


class GenericButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def setTriggerable(self, is_it: bool):
        self.___event_enabled = is_it

    def isTriggerable(self):
        return self.___event_enabled