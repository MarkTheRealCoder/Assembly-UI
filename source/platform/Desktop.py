from PyQt5.QtCore import QSize


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