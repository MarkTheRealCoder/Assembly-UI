from PyQt5.QtCore import QSize
from PyQt5.QtGui import QFont


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
    def getScalableFontSize(base_size: int = 12) -> int:
        """Calculate scalable font size based on screen size"""
        if Desktop.DESKTOP_SIZE is not None:
            # Use width as reference for scaling
            screen_width = Desktop.DESKTOP_SIZE.width()
            # Scale factor: 1.0 for 1920px width, adjust proportionally
            scale_factor = screen_width / 1920.0
            # Ensure minimum size of 8 and maximum of 24
            scaled_size = max(8, min(18, int(base_size * scale_factor)))
            return scaled_size
        return base_size

    @staticmethod
    def createScalableFont(family: str = "Anonymous Pro", base_size: int = 12, bold: bool = False) -> QFont:
        """Create a QFont with scalable size based on screen dimensions"""
        font = QFont(family)
        font.setPointSize(Desktop.getScalableFontSize(base_size))
        font.setBold(bold)
        return font