from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontMetrics, QPainter
from PyQt5.QtWidgets import QLabel, QSizePolicy


class TabLabel(QLabel):
    def __init__(self, parent, name: str):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Preferred)
        self.setText(name)
        self.configurations()
        # paintEvent elides long names, so the label can be narrower than its text.
        self.setMinimumWidth(1)
        self.setMaximumWidth(210)
        self.installEventFilter(self.parent())

    def sizeHint(self):
        # Calculate size based on actual text width + margins
        metrics = QFontMetrics(self.font())
        text_width = metrics.horizontalAdvance(self.text())
        margins = self.contentsMargins()

        return QSize(
            text_width + margins.left() + margins.right(),
            metrics.height()
        )

    def configurations(self):
        self.setObjectName("TabLabel")
        self.setContentsMargins(5, 0, 5, 0)
        self.setAlignment(Qt.AlignCenter)
        self.adjustSize()

    def paintEvent(self, event):
        painter = QPainter(self)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideLeft, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)

