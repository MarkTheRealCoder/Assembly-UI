from PyQt5.QtCore import QEvent, QMargins, QPoint, QRectF, Qt, QTimer, pyqtProperty
from PyQt5.QtGui import QBrush, QColor, QEnterEvent, QPainter, QPainterPath, QPen
from PyQt5.QtWidgets import QApplication, QFrame, QVBoxLayout, QWidget

from source.platform import isMac

from .gnome_tiling import TILED_RESIZE_EDGES_PROPERTY, watch_gnome_tiling
from .resize_cursor_linux import LinuxResizeCursors


_RESIZE_BORDER_WIDTH = 8 if isMac() else 5
_RESIZE_CORNER_EXTENT = 20
# Cocoa does not deliver mouse events on transparent pixels, so macOS has no outer band.
_FLOATING_RESIZE_OUTSET = 0 if isMac() else 8
_MANUAL_RESIZE_INTERVAL_MS = 16
_CORNER_RADIUS = 12
_INNER_SHADOW_WIDTH = 4
_ALL_RESIZE_EDGES = Qt.LeftEdge | Qt.TopEdge | Qt.RightEdge | Qt.BottomEdge


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
        self._resize_edges = Qt.Edges()
        self.resize_margins = QMargins()
        self.outset = 0
        self._manual_resize = None
        self._pending_resize_position = None
        self._manual_resize_timer = QTimer(self)
        self._manual_resize_timer.setSingleShot(True)
        self._manual_resize_timer.setTimerType(Qt.PreciseTimer)
        self._manual_resize_timer.timeout.connect(self._apply_manual_resize)
        self.setMouseTracking(True)

    def set_resize_edges(self, edges, outset):
        if self._resize_edges != edges or self.outset != outset:
            self._resize_edges = edges
            self.outset = outset
            width = _RESIZE_BORDER_WIDTH + outset
            self.resize_margins = QMargins(*(
                width if edges & side else 0
                for side in (Qt.LeftEdge, Qt.TopEdge, Qt.RightEdge, Qt.BottomEdge)
            ))
            self._clear_resize_cursor()
        self.setVisible(bool(edges))

    def _edges_at(self, pos):
        bounds = self.rect()
        edges = Qt.Edges()
        if not bounds.contains(pos) or bounds.marginsRemoved(self.resize_margins).contains(pos):
            return edges

        corner_extent = _RESIZE_CORNER_EXTENT + self.outset
        horizontal_corner = min(corner_extent, bounds.width() // 2)
        vertical_corner = min(corner_extent, bounds.height() // 2)
        if pos.x() < horizontal_corner:
            edges |= Qt.LeftEdge
        elif pos.x() >= bounds.width() - horizontal_corner:
            edges |= Qt.RightEdge
        if pos.y() < vertical_corner:
            edges |= Qt.TopEdge
        elif pos.y() >= bounds.height() - vertical_corner:
            edges |= Qt.BottomEdge
        return edges & self._resize_edges

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
        if cursor is not self._active_cursor:
            self._active_cursor = cursor
            self.setCursor(cursor)
        # Qt can change the window cursor even when the pointer stays on the same edge.
        window = self.window().windowHandle()
        if window is not None and window.cursor() != cursor:
            window.setCursor(cursor)

    def _clear_resize_cursor(self):
        cursor = self._active_cursor
        if cursor is None:
            return
        self._active_cursor = None
        self.unsetCursor()
        window = self.window().windowHandle()
        if window is not None and window.cursor() == cursor:
            window.unsetCursor()

    def _apply_manual_resize(self):
        position, self._pending_resize_position = self._pending_resize_position, None
        if self._manual_resize is None or position is None:
            return

        edges, origin, geometry = self._manual_resize
        delta = position - origin
        window = self.window()
        maximum = window.maximumSize()
        minimum = window.minimumSize().expandedTo(window.minimumSizeHint()).boundedTo(maximum)

        x, y, width, height = geometry.getRect()
        if edges & (Qt.LeftEdge | Qt.RightEdge):
            movement = -delta.x() if edges & Qt.LeftEdge else delta.x()
            width = max(minimum.width(), min(width + movement, maximum.width()))
            if edges & Qt.LeftEdge:
                x = geometry.right() + 1 - width
        if edges & (Qt.TopEdge | Qt.BottomEdge):
            movement = -delta.y() if edges & Qt.TopEdge else delta.y()
            height = max(minimum.height(), min(height + movement, maximum.height()))
            if edges & Qt.TopEdge:
                y = geometry.bottom() + 1 - height
        window.setGeometry(x, y, width, height)

    def _finish_manual_resize(self):
        self._manual_resize_timer.stop()
        self._pending_resize_position = None
        self._manual_resize = None

    def showEvent(self, event):
        self._prepare_cursors()
        super().showEvent(event)

    def enterEvent(self, event):
        if isinstance(event, QEnterEvent):
            self._update_resize_cursor(event.pos())
        super().enterEvent(event)

    def mouseMoveEvent(self, event):
        if self._manual_resize is not None:
            if event.buttons() & Qt.LeftButton:
                # Apply only the latest position on each frame.
                self._pending_resize_position = event.globalPos()
                if not self._manual_resize_timer.isActive():
                    self._manual_resize_timer.start(_MANUAL_RESIZE_INTERVAL_MS)
                event.accept()
                return
            self._finish_manual_resize()
        self._update_resize_cursor(event.pos())
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self._manual_resize is not None and event.button() == Qt.LeftButton:
            self._pending_resize_position = event.globalPos()
            self._apply_manual_resize()
            self._finish_manual_resize()
            self._update_resize_cursor(event.pos())
            event.accept()
            return
        super().mouseReleaseEvent(event)

    def leaveEvent(self, event):
        if self._manual_resize is None:
            self._clear_resize_cursor()
        super().leaveEvent(event)

    def hideEvent(self, event):
        self._finish_manual_resize()
        self._clear_resize_cursor()
        super().hideEvent(event)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            edges = self._edges_at(event.pos())
            window = self.window().windowHandle()
            if edges and window is not None:
                # Cocoa has no system resize, so Qt moves the edges there.
                if not window.startSystemResize(edges):
                    self._manual_resize = edges, event.globalPos(), self.window().geometry()
                event.accept()
                return
        super().mousePressEvent(event)


class ResizeFrame(QWidget):
    def __init__(self, window, content):
        super().__init__(window)
        self.setObjectName("ResizeFrame")
        self._frame_color = QColor("#1E1E1E")
        self._header_brush = QBrush(self._frame_color)
        self._toolbar = content.findChild(QFrame, "Toolbar", Qt.FindDirectChildrenOnly)
        self._tiled_resize_edges = None
        self._tiling_update_pending = False
        self._tiling_update_timer = QTimer(self)
        self._tiling_update_timer.setSingleShot(True)
        self._tiling_update_timer.timeout.connect(self._update_frame_state)
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
        tiled_edges = self._tiled_resize_edges
        restored = not (state & (Qt.WindowMaximized | Qt.WindowFullScreen | Qt.WindowMinimized))
        self._rounded = restored and tiled_edges is None
        resize_edges = _ALL_RESIZE_EDGES if tiled_edges is None else Qt.Edges(tiled_edges)
        outset = _FLOATING_RESIZE_OUTSET if self._rounded else 0
        self._resize_border.set_resize_edges(resize_edges if restored else Qt.Edges(), outset)
        self.layout().setContentsMargins(self._resize_border.resize_margins)
        self.update()

    def _queue_tiling_update(self, native_window):
        if not self._tiling_update_pending:
            return
        self._tiling_update_pending = False
        tiled_edges = native_window.property(TILED_RESIZE_EDGES_PROPERTY) if native_window is not None else None
        if tiled_edges != self._tiled_resize_edges:
            self._tiled_resize_edges = tiled_edges
            self._tiling_update_timer.start(0)

    def resizeEvent(self, event):
        self._resize_border.setGeometry(self.rect())
        super().resizeEvent(event)

    def paintEvent(self, event):
        painter = QPainter(self)
        # Keep the transparent resize band inside the surface that receives input.
        outset = self._resize_border.outset
        face = QRectF(self.rect()).adjusted(outset, outset, -outset, -outset)
        radius = _CORNER_RADIUS if self._rounded else 0
        painter.setRenderHint(QPainter.Antialiasing, self._rounded)
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
        if self._rounded:
            painter.setClipPath(outline)
            painter.setBrush(Qt.NoBrush)
            for depth in range(_INNER_SHADOW_WIDTH):
                inset = depth + 0.5
                shade = face.adjusted(inset, inset, -inset, -inset)
                shade_radius = radius - inset
                painter.setPen(QPen(QColor(0, 0, 0, 56 - 12 * depth)))
                painter.drawRoundedRect(shade, shade_radius, shade_radius)
            painter.strokePath(outline, QPen(QColor(255, 255, 255, 30)))

    def _sync_content_cursor(self, native_window, pos):
        if QApplication.overrideCursor() is not None or QApplication.activePopupWidget() is not None:
            return
        if QWidget.mouseGrabber() is not None:
            return
        widget = self.window().childAt(pos)
        if widget is None or widget is self._resize_border:
            return

        # Pointer events also arrive when another window has keyboard focus.
        cursor = widget.cursor()
        if native_window.cursor() != cursor:
            native_window.setCursor(cursor)

    def eventFilter(self, watched, event):
        event_type = event.type()
        window = self.window()
        if watched is window:
            if event_type == QEvent.WindowStateChange:
                self._update_frame_state()
            elif event_type == QEvent.Resize:
                self._queue_tiling_update(window.windowHandle())
            elif event_type in (QEvent.WinIdChange, QEvent.Show):
                self._tiling_update_pending = True
                native_window = window.windowHandle()
                if native_window is not None:
                    native_window.installEventFilter(self)
                    watch_gnome_tiling(native_window)
        elif watched is self._toolbar and event_type in (QEvent.Move, QEvent.Resize, QEvent.Show, QEvent.Hide):
            self.update()
        elif watched is window.windowHandle():
            if (event_type == QEvent.DynamicPropertyChange and
                    event.propertyName() == TILED_RESIZE_EDGES_PROPERTY.encode("ascii")):
                # GTK sends the edges before Qt can apply the XDG surface geometry.
                self._tiling_update_pending = True
            elif event_type == QEvent.Expose and not event.region().isEmpty():
                self._queue_tiling_update(watched)
            elif isinstance(event, QEnterEvent) or (event_type == QEvent.MouseMove and event.buttons() == Qt.NoButton):
                self._sync_content_cursor(watched, event.pos())
        return super().eventFilter(watched, event)


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
