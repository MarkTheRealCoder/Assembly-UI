from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from PyQt5.QtWidgets import QLineEdit


class HexCodeColorLineGraphics(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("CPHexConverter")
        self.setMaxLength(7) # e.g., #FFFFFF
        self.setFont(QFont("Monospace", 10))
        self.setAlignment(Qt.AlignCenter | Qt.AlignVCenter)


class HexCodeColorLineLogic(HexCodeColorLineGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class HexCodeColorLine(HexCodeColorLineLogic):
    def __init__(self, parent):
        super().__init__(parent)
