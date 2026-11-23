from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget


_RESIZE_BORDER_WIDTH = 5
_RESIZE_POSITIONS = ("topleft", "top", "topright", "left", "right", "bottomleft", "bottom", "bottomright")


class BaseWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windowEffect = None
        self.MAXBUTTON_RECT = lambda: (0, 0, 0, 0)
        self._mouse_on_max_btn = False
        self._resize_frames = []

    def setFrameless(self, hint=None, flags: list = None):
        if flags is None:
            flags = []
        newFlags = self.windowFlags() | Qt.FramelessWindowHint
        for flag in flags:
            newFlags |= flag
        self.setWindowFlags(newFlags)

        # Cocoa has no startSystemResize, so the existing frames resize the window from Qt.
        from source.interface.shared import DraggableFrame

        self._resize_frames = [DraggableFrame(self, position) for position in _RESIZE_POSITIONS]

    def _placeResizeFrames(self):
        border = _RESIZE_BORDER_WIDTH
        width, height = self.width(), self.height()
        visible = not self.isFullScreen()
        for frame in self._resize_frames:
            position = frame.position
            x = width - border if position & 8 else (0 if position & 4 else border)
            y = height - border if position & 2 else (0 if position & 1 else border)
            frame_width = border if position & 12 else width - 2 * border
            frame_height = border if position & 3 else height - 2 * border
            frame.setGeometry(x, y, frame_width, frame_height)
            frame.setVisible(visible)
            frame.raise_()

    def resizeEvent(self, event):
        self._placeResizeFrames()
        super().resizeEvent(event)

    def _onScreenChanged(self):
        pass


def native_maximize(widget: QWidget):
    QWidget.showMaximized(widget)


def native_restore(widget: QWidget):
    QWidget.showNormal(widget)


def native_minimize(widget: QWidget):
    QWidget.showMinimized(widget)
