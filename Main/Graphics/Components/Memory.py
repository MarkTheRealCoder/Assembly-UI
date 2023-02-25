from PyQt5.QtWidgets import QLabel, QWidget


class Memory(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__(parent=mwt)
        self.setConfigurations()
        self.setObjectName("Memory")

    def setConfigurations(self):
        self.setFixedWidth(528)
        self.setFixedHeight(508)


class MemoryOptions(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__(parent=mwt)
        self.setConfigurations()
        self.setObjectName("Options")

    def setConfigurations(self):
        self.setFixedWidth(528)
        self.setFixedHeight(110)

