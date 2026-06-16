from PyQt5.QtCore import Qt, QEvent, QPoint, QTimer
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget, QApplication

from source.platform.adaptability import isMac


class BaseWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windowEffect = None
        self.___border_width = 5
        self.MAXBUTTON_RECT = lambda: (100, 100, 10, 10)
        self._mouse_on_max_btn = False
        self._resize_edges = None
        self._resize_drag_pos = None
        self._resize_cursor_override = False
        self._system_move_active = False
        self._syncing_geometry = False
        self._geometry_sync_connected = False
        self._mac_frameless_pending = False

    def setFrameless(self, hint=None, flags: list = None):
        if flags is None:
            flags = []

        if isMac():
            newFlags = self.windowFlags()
            for flag in flags:
                newFlags |= flag
            self.setWindowFlags(newFlags)
            self._mac_frameless_pending = True
            return

        newFlags = self.windowFlags() | Qt.FramelessWindowHint
        for flag in flags:
            newFlags |= flag
        self.setWindowFlags(newFlags)

        app = QApplication.instance()
        if app:
            app.installEventFilter(self)

    def showEvent(self, event):
        super().showEvent(event)
        if isMac() and self._mac_frameless_pending:
            self._applyMacNativeFrameless()
            self._mac_frameless_pending = False
        self._ensureNativeGeometrySync()

    def changeEvent(self, event):
        if isMac() and event.type() == QEvent.WindowStateChange:
            QTimer.singleShot(0, self._applyMacNativeFrameless)
        super().changeEvent(event)

    def _applyMacNativeFrameless(self):
        if not self.winId():
            return
        from source.interface.templates.window.macos_native import configure_hidden_titlebar

        configure_hidden_titlebar(self)

    def startSystemMove(self):
        handle = self.windowHandle()
        if not handle:
            return False
        if handle.startSystemMove():
            self._system_move_active = True
            return True
        return False

    def _ensureNativeGeometrySync(self):
        if self._geometry_sync_connected:
            return
        handle = self.windowHandle()
        if not handle:
            return
        handle.xChanged.connect(self._syncNativeGeometry)
        handle.yChanged.connect(self._syncNativeGeometry)
        handle.widthChanged.connect(self._syncNativeGeometry)
        handle.heightChanged.connect(self._syncNativeGeometry)
        handle.windowStateChanged.connect(self._onNativeWindowStateChanged)
        self._geometry_sync_connected = True

    def _syncNativeGeometry(self, *_args):
        if self._resize_edges is not None or self._syncing_geometry:
            return
        handle = self.windowHandle()
        if not handle:
            return
        native = handle.geometry()
        if self.geometry() == native:
            return
        self._syncing_geometry = True
        try:
            self.setGeometry(native)
        finally:
            self._syncing_geometry = False

    def _onNativeWindowStateChanged(self, _state):
        self._syncNativeGeometry()

    def _scheduleSystemMoveFinish(self):
        for delay in (0, 50, 150, 350):
            QTimer.singleShot(delay, self._finishSystemMove)

    def _finishSystemMove(self):
        if self._resize_edges is not None:
            return
        self._syncNativeGeometry()

    def moveEvent(self, event):
        super().moveEvent(event)
        if self._system_move_active:
            self._syncNativeGeometry()

    def eventFilter(self, watched, event):
        if isMac():
            return False

        if not self.isVisible() or self.isMaximized() or self.isFullScreen():
            if self._resize_edges is not None:
                self._endManualResize()
            else:
                self._clearResizeCursor()
            return False

        event_type = event.type()

        if event_type == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if not self._pointerTargetsSelf(event.globalPos()):
                return False
            edges = self._resizeEdges(self.mapFromGlobal(event.globalPos()))
            if not edges:
                return False
            handle = self.windowHandle()
            if handle and handle.startSystemResize(edges):
                return True
            self._resize_edges = edges
            self._resize_drag_pos = event.globalPos()
            return True

        if event_type == QEvent.MouseMove:
            if self._resize_edges is not None and event.buttons() & Qt.LeftButton:
                self._applyManualResize(event.globalPos())
                return True
            if self._pointerTargetsSelf(event.globalPos()):
                self._updateResizeCursor(self._resizeEdges(self.mapFromGlobal(event.globalPos())))
            else:
                self._clearResizeCursor()
            return False

        if event_type == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self._resize_edges is not None:
                self._endManualResize()
            elif self._system_move_active:
                self._system_move_active = False
                self._scheduleSystemMoveFinish()
            return False

        return False

    def _pointerTargetsSelf(self, global_pos):
        if not self.frameGeometry().contains(global_pos):
            return False
        widget_at = QApplication.widgetAt(global_pos)
        if widget_at is None:
            return True
        return widget_at.window() is self

    def _resizeEdges(self, pos):
        w, h = self.width(), self.height()
        x, y = pos.x(), pos.y()
        bw = self.___border_width
        left = x < bw
        top = y < bw
        right = x > w - bw
        bottom = y > h - bw

        edges = Qt.Edges(0)
        if top:
            edges |= Qt.TopEdge
        if bottom:
            edges |= Qt.BottomEdge
        if left:
            edges |= Qt.LeftEdge
        if right:
            edges |= Qt.RightEdge
        return edges if edges else None

    def _cursorForEdges(self, edges):
        if not edges:
            return Qt.ArrowCursor
        top = bool(edges & Qt.TopEdge)
        bottom = bool(edges & Qt.BottomEdge)
        left = bool(edges & Qt.LeftEdge)
        right = bool(edges & Qt.RightEdge)
        if top and left:
            return Qt.SizeFDiagCursor
        if top and right:
            return Qt.SizeBDiagCursor
        if bottom and left:
            return Qt.SizeBDiagCursor
        if bottom and right:
            return Qt.SizeFDiagCursor
        if top or bottom:
            return Qt.SizeVerCursor
        if left or right:
            return Qt.SizeHorCursor
        return Qt.ArrowCursor

    def _updateResizeCursor(self, edges):
        cursor = self._cursorForEdges(edges)
        if cursor == Qt.ArrowCursor:
            self._clearResizeCursor()
            return
        if self._resize_cursor_override:
            QApplication.changeOverrideCursor(QCursor(cursor))
        else:
            QApplication.setOverrideCursor(QCursor(cursor))
            self._resize_cursor_override = True

    def _clearResizeCursor(self):
        if self._resize_cursor_override:
            QApplication.restoreOverrideCursor()
            self._resize_cursor_override = False

    def _applyManualResize(self, global_pos):
        difference = self._resize_drag_pos - global_pos
        geo = self.frameGeometry()
        x, y = geo.x(), geo.y()
        w, h = geo.width(), geo.height()
        edges = self._resize_edges
        ew, eh = False, False

        if edges & Qt.TopEdge:
            new_height = h + difference.y()
            if new_height < self.minimumHeight():
                difference.setY(self.minimumHeight() - h)
                new_height = self.minimumHeight()
                eh = True
            y -= difference.y()
            h = new_height
        elif edges & Qt.BottomEdge:
            new_height = h - difference.y()
            if new_height < self.minimumHeight():
                new_height = self.minimumHeight()
                eh = True
            h = new_height

        if edges & Qt.LeftEdge:
            new_width = w + difference.x()
            if new_width < self.minimumWidth():
                difference.setX(self.minimumWidth() - w)
                new_width = self.minimumWidth()
                ew = True
            x -= difference.x()
            w = new_width
        elif edges & Qt.RightEdge:
            new_width = w - difference.x()
            if new_width < self.minimumWidth():
                new_width = self.minimumWidth()
                ew = True
            w = new_width

        self.setGeometry(x, y, w, h)
        self._resize_drag_pos = self._resizeDragPosition(global_pos, ew, eh)

    def _resizeDragPosition(self, global_pos, ew, eh):
        if not (ew or eh):
            return global_pos
        geo = self.frameGeometry()
        edges = self._resize_edges
        x, y = global_pos.x(), global_pos.y()
        if ew:
            x = geo.left() if edges & Qt.LeftEdge else geo.right()
        if eh:
            y = geo.top() if edges & Qt.TopEdge else geo.bottom()
        return QPoint(x, y)

    def _endManualResize(self):
        self._resize_edges = None
        self._resize_drag_pos = None

    def closeEvent(self, event):
        self._clearResizeCursor()
        app = QApplication.instance()
        if app and not isMac():
            app.removeEventFilter(self)
        super().closeEvent(event)

    def _onScreenChanged(self):
        pass


def native_maximize(widget: QWidget):
    QWidget.showMaximized(widget)


def native_restore(widget: QWidget):
    QWidget.showNormal(widget)


def native_minimize(widget: QWidget):
    QWidget.showMinimized(widget)
