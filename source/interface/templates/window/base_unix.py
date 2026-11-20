from PyQt5.QtCore import QEvent, QPoint, QRectF, Qt, pyqtProperty
from PyQt5.QtGui import QBrush, QColor, QEnterEvent, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QFrame, QVBoxLayout, QWidget

from .resize_cursor_linux import LinuxResizeCursors


_RESIZE_BORDER_WIDTH = 10
_RESIZE_CORNER_EXTENT = 20
_CORNER_RADIUS = 12
_SHADOW_WIDTH = 4


class _ResizeBorder(QWidget):
    _CURSOR_SPECS = (
        (Qt.TopEdge | Qt.LeftEdge, "nw-resize", Qt.SizeFDiagCursor),
        (Qt.TopEdge, "n-resize", Qt.SizeVerCursor),
        (Qt.TopEdge | Qt.RightEdge, "ne-resize", Qt.SizeBDiagCursor),
        (Qt.LeftEdge, "w-resize", Qt.SizeHorCursor),
        (Qt.RightEdge, "e-resize", Qt.SizeHorCursor),
        (Qt.BottomEdge | Qt.LeftEdge, "sw-resize", Qt.SizeBDiagCursor),
        (Qt.BottomEdge, "s-resize", Qt.SizeVerCursor),
        (Qt.BottomEdge | Qt.RightEdge, "se-resize", Qt.SizeFDiagCursor),
    )

    def __init__(self, parent):
        super().__init__(parent)
        self._cursors = LinuxResizeCursors()
        self._direction_cursors = {}
        self._cursor_scale = None
        self._active_cursor = None
        self.setMouseTracking(True)

    def _edges_at(self, pos):
        border = _RESIZE_BORDER_WIDTH
        bounds = self.rect()
        edges = Qt.Edges()
        if not bounds.contains(pos) or bounds.adjusted(border, border, -border, -border).contains(pos):
            return edges

        horizontal_corner = min(_RESIZE_CORNER_EXTENT, bounds.width() // 2)
        vertical_corner = min(_RESIZE_CORNER_EXTENT, bounds.height() // 2)
        if pos.x() < horizontal_corner:
            edges |= Qt.LeftEdge
        elif pos.x() >= bounds.width() - horizontal_corner:
            edges |= Qt.RightEdge
        if pos.y() < vertical_corner:
            edges |= Qt.TopEdge
        elif pos.y() >= bounds.height() - vertical_corner:
            edges |= Qt.BottomEdge
        return edges

    def _prepare_cursors(self):
        scale = self.devicePixelRatioF()
        if scale != self._cursor_scale:
            self._direction_cursors = {
                int(edges): self._cursors.cursor(name, fallback, scale)
                for edges, name, fallback in self._CURSOR_SPECS
            }
            self._cursor_scale = scale

    def _update_resize_cursor(self, pos):
        edges = self._edges_at(pos)
        if not edges:
            self._clear_resize_cursor()
            return
        self._prepare_cursors()
        cursor = self._direction_cursors[int(edges)]
        if cursor is self._active_cursor:
            return
        self._active_cursor = cursor
        self.setCursor(cursor)
        if not self.underMouse():
            # Qt can deliver the first move before marking the border as hovered.
            window = self.window().windowHandle()
            if window is not None:
                window.setCursor(cursor)

    def _clear_resize_cursor(self):
        if self._active_cursor is None:
            return
        self._active_cursor = None
        self.unsetCursor()
        window = self.window().windowHandle()
        if window is not None:
            window.unsetCursor()

    def showEvent(self, event):
        self._prepare_cursors()
        super().showEvent(event)

    def enterEvent(self, event):
        if isinstance(event, QEnterEvent):
            self._update_resize_cursor(event.pos())
        super().enterEvent(event)

    def mouseMoveEvent(self, event):
        self._update_resize_cursor(event.pos())
        super().mouseMoveEvent(event)

    def leaveEvent(self, event):
        self._clear_resize_cursor()
        super().leaveEvent(event)

    def hideEvent(self, event):
        self._clear_resize_cursor()
        super().hideEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edges = self._edges_at(event.pos())
            window = self.window().windowHandle()
            if edges and window is not None and window.startSystemResize(edges):
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
        layout = QVBoxLayout(self)
        layout.setSpacing(0)
        layout.addWidget(content)

        # The content covers the center, leaving one continuous mouse target on the rim.
        self._resize_border = _ResizeBorder(self)
        self._resize_border.stackUnder(content)
        self._resize_border.setGeometry(self.rect())

        self._update_frame_state()
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

    def _update_frame_state(self):
        state = self.window().windowState()
        self._has_border = not (state & (Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized))
        margin = _RESIZE_BORDER_WIDTH if self._has_border else 0
        self.layout().setContentsMargins(margin, margin, margin, margin)
        self._resize_border.setVisible(self._has_border)
        self.update()

    def resizeEvent(self, event):
        self._resize_border.setGeometry(self.rect())
        super().resizeEvent(event)

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
            self._update_frame_state()
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
