from PyQt5.QtCore import QSize
from PyQt5.QtWidgets import QPushButton, QSizePolicy


class Button(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)

        self.___placeholder = lambda: None

        self.configurations()

        self.clicked.connect(lambda: self.___placeholder())

    def configurations(self):
        self.setObjectName("FileButton")
        self.setFixedHeight(30)
        self.setFixedWidth(30)
        self.setIconSize(QSize(20, 20))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

    def onClick(self, func: callable):
        if not callable(func):
            raise TypeError("func must be callable")
        self.___placeholder = func