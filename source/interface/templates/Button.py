from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap, QPainter, QColor, QIcon
from PyQt5.QtWidgets import QPushButton, QSizePolicy


class GenericButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def rerenderIcon(self, icon, color: str):
        pixmap = icon.pixmap(32, 32)  # render to 32x32 px pixmap

        # Create a colored version
        colored = QPixmap(pixmap.size())
        colored.fill(Qt.GlobalColor.transparent)

        p = QPainter(colored)
        p.drawPixmap(0, 0, pixmap)  # draw original
        p.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
        p.fillRect(colored.rect(), QColor(color))  # your tint color
        p.end()

        return QIcon(colored)

