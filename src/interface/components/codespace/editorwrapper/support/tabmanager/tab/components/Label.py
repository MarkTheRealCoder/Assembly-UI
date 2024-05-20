from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontMetrics, QPainter
from PyQt5.QtWidgets import QLabel, QSizePolicy


class TabLabel(QLabel):
    def __init__(self, parent, name: str):
        super().__init__(parent)
        self.configurations()
        self.setText(name)
        self.installEventFilter(self.parent())

    def configurations(self):
        self.setObjectName("TabLabel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)
        self.setAlignment(Qt.AlignCenter)

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideLeft, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

