from PyQt5.QtWidgets import QTextEdit, QWidget


class Input(QTextEdit):
    def __init__(self, mwt: QWidget):
        super(QTextEdit, self).__init__(mwt)
        self.setObjectName("Input")
