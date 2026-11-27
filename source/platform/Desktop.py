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
    def getScaleFactor(widget=None) -> float:
        """Return the UI scale for the screen of a widget, where 1920x1080 is 1.0"""
        screen = widget.window().screen() if widget is not None else QGuiApplication.primaryScreen()
        size = screen.size()
        return max(0.85, min(2.0, min(size.width() / 1920, size.height() / 1080)))

    @staticmethod
    def getPointScale() -> float:
        """Return the factor that gives a point size the same visual size on each OS"""
        # macOS uses 72 logical DPI. Windows and Linux use 96 and apply the system scale.
        return 96 / 72 if isMac() else 1.0

    @staticmethod
    def getScalableFontSize(base_size: int = 12) -> int:
        """Calculate a font size that has the same visual size on each OS"""
        return max(8, min(18, round(base_size * Desktop.getPointScale())))

    @staticmethod
    def createScalableFont(family: str = "Anonymous Pro", base_size: int = 12, bold: bool = False) -> QFont:
        """Create a QFont with scalable size based on screen dimensions"""
        font = QFont(family)
        font.setPointSize(Desktop.getScalableFontSize(base_size))
        font.setBold(bold)
        return font