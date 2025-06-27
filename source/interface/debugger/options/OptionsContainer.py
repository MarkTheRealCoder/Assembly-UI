from PyQt5.QtWidgets import QLabel, QWidget


class OptionsContainer(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__(parent=mwt)
        self.setObjectName("Options")