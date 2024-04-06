from PyQt5.QtWidgets import QWidget, QLabel


class Output(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__(mwt)
        self.setObjectName("Output")
