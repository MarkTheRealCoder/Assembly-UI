from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel


class ColorLabelGraphics(QLabel):
    def __init__(self, parent, title):
        super().__init__(parent)
        self.setObjectName("CPLabel")
        self.setText(title)
        self.setMinimumWidth(200)
        self.setAlignment(Qt.AlignVCenter | Qt.AlignRight)


class ColorLabel(ColorLabelGraphics):
    def __init__(self, parent, title):
        super().__init__(parent, title)
