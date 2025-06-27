from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy


class FragmentLabel(QLabel):
    def __init__(self, parent: QWidget, v: str, is_key: bool = False):
        super().__init__(parent)
        self.setObjectName("KeyLabel" if is_key else "ValueLabel")
        self.setText(v)
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)