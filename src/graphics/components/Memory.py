from PyQt5.QtWidgets import QLabel, QWidget
from src.tools.Tools import SCALE, SCALEH


class Memory(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__(parent=mwt)
        self.setConfigurations()
        self.setObjectName("Memory")

    def setConfigurations(self):
        self.setFixedWidth(SCALE(528, self.parent().width()))
        self.setFixedHeight(SCALEH(508, self.parent().height()))


class MemoryOptions(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__(parent=mwt)
        self.setConfigurations()
        self.setObjectName("Options")

    def setConfigurations(self):
        self.setFixedWidth(SCALE(528, self.parent().width()))
        self.setFixedHeight(SCALEH(110, self.parent().height()))

