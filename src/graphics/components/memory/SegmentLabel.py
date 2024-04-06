from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy


class MemoryLabel(QLabel):
    def __init__(self, parent, content: str):
        super(QLabel, self).__init__(parent)
        self.setObjectName("MemoryLabel")
        self.setText(content)
        self.setAlignment(Qt.AlignCenter)
        self.setConfigurations()

    def setConfigurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)