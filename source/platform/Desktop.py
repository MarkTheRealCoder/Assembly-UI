from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont, QGuiApplication

from .adaptability import isMac


class Desktop:
    DESKTOP_SIZE: QSize = None

    @staticmethod
    def sizeHint(wr: float, hr: float) -> QSize or None:
        if Desktop.DESKTOP_SIZE is not None:
            ds = Desktop.DESKTOP_SIZE
            return QSize(int(ds.width() * wr), int(ds.height() * hr))
        return None

    @staticmethod
    def getDesktopSize() -> QSize:
        return Desktop.DESKTOP_SIZE

    @staticmethod
    def setDesktopSize(size: QSize):
        if isinstance(size, QSize):
            Desktop.DESKTOP_SIZE = size

    @staticmethod
    def centerWidget(widget, anchor=None):
        """Center a window on the screen of the anchor, or on the primary screen"""
        screen = anchor.window().screen() if anchor is not None else QGuiApplication.primaryScreen()
        frame = widget.frameGeometry()
        frame.moveCenter(screen.availableGeometry().center())
        widget.move(frame.topLeft())

    @staticmethod
    def getScalableFontSize(base_size: int = 12) -> int:
        """Calculate a font size that has the same visual size on each OS"""
        # macOS uses 72 logical DPI. Windows and Linux use 96 and apply the system scale.
        scaled_size = base_size * 96 / 72 if isMac() else base_size
        return max(8, min(18, round(scaled_size)))

    @staticmethod
    def createScalableFont(family: str = "Anonymous Pro", base_size: int = 12, bold: bool = False) -> QFont:
        """Create a QFont with scalable size based on screen dimensions"""
        font = QFont(family)
        font.setPointSize(Desktop.getScalableFontSize(base_size))
        font.setBold(bold)
        return font