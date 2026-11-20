from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QGridLayout, QWidget


_RESIZE_BORDER_WIDTH = 5


class _ResizeHandle(QWidget):
    def __init__(self, parent, edges, cursor):
        super().__init__(parent)
        self._edges = edges
        self.setCursor(cursor)
        if edges & (Qt.TopEdge | Qt.BottomEdge):
            self.setFixedHeight(_RESIZE_BORDER_WIDTH)
        if edges & (Qt.LeftEdge | Qt.RightEdge):
            self.setFixedWidth(_RESIZE_BORDER_WIDTH)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handle = self.window().windowHandle()
            if handle is not None and handle.startSystemResize(self._edges):
                event.accept()
                return
        super().mousePressEvent(event)


class LinuxResizeFrame(QWidget):
    def __init__(self, window, content):
        super().__init__(window)
        layout = QGridLayout(self)
        layout.setOriginCorner(Qt.TopRightCorner if self.isRightToLeft() else Qt.TopLeftCorner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 1)
        layout.addWidget(content, 1, 1)

        self._handles = []
        for row, column, edges, cursor in (
            (0, 0, Qt.TopEdge | Qt.LeftEdge, Qt.SizeFDiagCursor),
            (0, 1, Qt.TopEdge, Qt.SizeVerCursor),
            (0, 2, Qt.TopEdge | Qt.RightEdge, Qt.SizeBDiagCursor),
            (1, 0, Qt.LeftEdge, Qt.SizeHorCursor),
            (1, 2, Qt.RightEdge, Qt.SizeHorCursor),
            (2, 0, Qt.BottomEdge | Qt.LeftEdge, Qt.SizeBDiagCursor),
            (2, 1, Qt.BottomEdge, Qt.SizeVerCursor),
            (2, 2, Qt.BottomEdge | Qt.RightEdge, Qt.SizeFDiagCursor),
        ):
            handle = _ResizeHandle(self, edges, cursor)
            layout.addWidget(handle, row, column)
            self._handles.append(handle)

        self._update_handle_visibility()
        window.installEventFilter(self)

    def _update_handle_visibility(self):
        state = self.window().windowState()
        can_resize = not (state & (Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized))
        for handle in self._handles:
            handle.setVisible(can_resize)

    def eventFilter(self, watched, event):
        if event.type() == QEvent.WindowStateChange and watched is self.window():
            self._update_handle_visibility()
        return super().eventFilter(watched, event)


class BaseWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windowEffect = None
        self.MAXBUTTON_RECT = lambda: (100, 100, 10, 10)
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
