from PyQt5.QtCore import QEvent, QPoint, QRectF, Qt, pyqtProperty
from PyQt5.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QFrame, QGridLayout, QWidget

from .resize_cursor_linux import LinuxResizeCursors


_RESIZE_BORDER_WIDTH = 10
_CORNER_RADIUS = 12
_SHADOW_WIDTH = 4


class _ResizeHandle(QWidget):
    def __init__(self, parent, edges, cursors, cursor_name, fallback_cursor):
        super().__init__(parent)
        self._edges = edges
        self._cursors = cursors
        self._cursor_name = cursor_name
        self._fallback_cursor = fallback_cursor
        self.setMouseTracking(True)
        if edges & (Qt.TopEdge | Qt.BottomEdge):
            self.setFixedHeight(_RESIZE_BORDER_WIDTH)
        if edges & (Qt.LeftEdge | Qt.RightEdge):
            self.setFixedWidth(_RESIZE_BORDER_WIDTH)

    def _show_resize_cursor(self):
        cursor = self._cursors.cursor(self._cursor_name, self._fallback_cursor, self.devicePixelRatioF())
        self.setCursor(cursor)
        # The first pointer move can arrive before Qt marks the handle as hovered.
        window = self.window().windowHandle()
        if window is not None:
            window.setCursor(cursor)

    def _clear_resize_cursor(self):
        if not self.testAttribute(Qt.WA_SetCursor):
            return
        self.unsetCursor()
        window = self.window().windowHandle()
        if window is not None:
            window.unsetCursor()

    def enterEvent(self, event):
        self._show_resize_cursor()
        super().enterEvent(event)

    def mouseMoveEvent(self, event):
        if not self.rect().contains(event.pos()):
            self._clear_resize_cursor()
        elif not self.testAttribute(Qt.WA_SetCursor):
            self._show_resize_cursor()
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._clear_resize_cursor()
        super().leaveEvent(event)

    def hideEvent(self, event):
        self._clear_resize_cursor()
        super().hideEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            handle = self.window().windowHandle()
            if handle is not None and handle.startSystemResize(self._edges):
                self._clear_resize_cursor()
                event.accept()
                return
        super().mousePressEvent(event)


class LinuxResizeFrame(QWidget):
    def __init__(self, window, content):
        super().__init__(window)
        self.setObjectName("LinuxResizeFrame")
        self._frame_color = QColor("#1E1E1E")
        self._header_brush = QBrush(self._frame_color)
        self._toolbar = content.findChild(QFrame, "Toolbar", Qt.FindDirectChildrenOnly)
        layout = QGridLayout(self)
        layout.setOriginCorner(Qt.TopRightCorner if self.isRightToLeft() else Qt.TopLeftCorner)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setRowStretch(1, 1)
        layout.setColumnStretch(1, 1)
        layout.addWidget(content, 1, 1)

        self._handles = []
        cursors = LinuxResizeCursors()
        for row, column, edges, cursor_name, fallback_cursor in (
            (0, 0, Qt.TopEdge | Qt.LeftEdge, "nw-resize", Qt.SizeFDiagCursor),
            (0, 1, Qt.TopEdge, "n-resize", Qt.SizeVerCursor),
            (0, 2, Qt.TopEdge | Qt.RightEdge, "ne-resize", Qt.SizeBDiagCursor),
            (1, 0, Qt.LeftEdge, "w-resize", Qt.SizeHorCursor),
            (1, 2, Qt.RightEdge, "e-resize", Qt.SizeHorCursor),
            (2, 0, Qt.BottomEdge | Qt.LeftEdge, "sw-resize", Qt.SizeBDiagCursor),
            (2, 1, Qt.BottomEdge, "s-resize", Qt.SizeVerCursor),
            (2, 2, Qt.BottomEdge | Qt.RightEdge, "se-resize", Qt.SizeFDiagCursor),
        ):
            handle = _ResizeHandle(self, edges, cursors, cursor_name, fallback_cursor)
            layout.addWidget(handle, row, column)
            self._handles.append(handle)

        self._update_handle_visibility()
        window.installEventFilter(self)
        if self._toolbar is not None:
            self._toolbar.installEventFilter(self)

    @pyqtProperty(QColor)
    def frameColor(self):
        return self._frame_color

    @frameColor.setter
    def frameColor(self, color):
        self._frame_color = color
        self.update()

    @pyqtProperty(QBrush)
    def headerBrush(self):
        return self._header_brush

    @headerBrush.setter
    def headerBrush(self, brush):
        self._header_brush = brush
        self.update()

    def _update_handle_visibility(self):
        state = self.window().windowState()
        self._has_border = not (state & (Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized))
        for handle in self._handles:
            handle.setVisible(self._has_border)
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        face = QRectF(self.rect())
        radius = 0
        if self._has_border:
            painter.setRenderHint(QPainter.Antialiasing)
            painter.setPen(Qt.NoPen)
            face.adjust(_SHADOW_WIDTH, _SHADOW_WIDTH, -_SHADOW_WIDTH, -_SHADOW_WIDTH)
            radius = _CORNER_RADIUS
            for spread in range(_SHADOW_WIDTH, 0, -1):
                shadow = face.adjusted(-spread, -spread, spread, spread)
                painter.setBrush(QColor(0, 0, 0, 12 + 7 * (_SHADOW_WIDTH - spread)))
                painter.drawRoundedRect(shadow, radius + spread, radius + spread)

        outline = QPainterPath()
        outline.addRoundedRect(face, radius, radius)
        painter.fillPath(outline, self._frame_color)
        if self._toolbar is not None and not self._toolbar.isHidden():
            bottom = self._toolbar.mapTo(self, QPoint(0, self._toolbar.height() - 1)).y()
            header = QRectF(face.left(), face.top(), face.width(), bottom - face.top())
            painter.save()
            painter.setClipRect(header)
            painter.fillPath(outline, self._header_brush)
            painter.restore()
        if self._has_border:
            painter.strokePath(outline, QPen(QColor(255, 255, 255, 30)))

    def eventFilter(self, watched, event):
        if event.type() == QEvent.WindowStateChange and watched is self.window():
            self._update_handle_visibility()
        elif watched is self._toolbar and event.type() in (QEvent.Move, QEvent.Resize, QEvent.Show, QEvent.Hide):
            self.update()
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
