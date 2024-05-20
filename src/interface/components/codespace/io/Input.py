from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTextEdit, QWidget


class Input(QTextEdit):
    def __init__(self, mwt: QWidget):
        super(QTextEdit, self).__init__(mwt)
        self.setObjectName("Input")
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
