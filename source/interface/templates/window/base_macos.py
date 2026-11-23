from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget


class BaseWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windowEffect = None
        self.MAXBUTTON_RECT = lambda: (0, 0, 0, 0)
        self._mouse_on_max_btn = False

    def setFrameless(self, hint=None, flags: list = None):
        if flags is None:
            flags = []
        newFlags = self.windowFlags() | Qt.FramelessWindowHint
        for flag in flags:
            newFlags |= flag
        self.setWindowFlags(newFlags)

    def _onScreenChanged(self):
        pass


def native_maximize(widget: QWidget):
    QWidget.showMaximized(widget)


def native_restore(widget: QWidget):
    QWidget.showNormal(widget)


def native_minimize(widget: QWidget):
    QWidget.showMinimized(widget)
