import os
from typing import Optional

from PyQt5.QtCore import Qt, QEvent, QSettings, QByteArray, QSize
from PyQt5.QtWidgets import QWidget, QLayout, QSizePolicy, QSplitter, QSplitterHandle

from source.comms import Variable, Database
from source.filesystem import settings_path


class Settings:
    SETTINGS = QSettings(settings_path(), QSettings.IniFormat)
    SIGNAL = Variable(str)

    @staticmethod
    def get(key: str, default=None, _type: type = None):
        return Settings.SETTINGS.value(key, default) if _type is None else Settings.SETTINGS.value(key, default, _type)

    @staticmethod
    def getOrExcept(key: str, _type: type = None, error_message: str = None):
        """ Gets a value or raises an exception if it doesn't exist """
        value = Settings.get(key, None, _type)
        if value is None:
            if error_message is None:
                raise KeyError(f"Setting '{key}' not found")
            else:
                raise Exception(f"{error_message}")
        return value

    @staticmethod
    def set(key: str, value):
        """ Sets a value and emits the signal """
        Settings.SETTINGS.setValue(key, value)
        Settings.SIGNAL.setValue(key)

    @staticmethod
    def silentSet(key: str, value):
        """ Sets a value without emitting the signal """
        Settings.SETTINGS.setValue(key, value)

    @staticmethod
    def remove(key: str):
        """ Removes a setting """
        Settings.SETTINGS.remove(key)
        Settings.SETTINGS.sync()

    @staticmethod
    def addNotificationGroup(name: str, callback: callable):
        """ Calls the callback when a setting with the given name (or starting with it) changes """
        Settings.SIGNAL.connect(lambda: callback() if Settings.SIGNAL.getValue() == name else None)

    @staticmethod
    def base_dir() -> str:
        path = Settings.SETTINGS.value("application/basedir")
        if not path:
            path = os.path.expanduser("~")
            Settings.silentSet("application/basedir", path)
        return path

    @staticmethod
    def sync():
        """ Syncs the settings to the file """
        Settings.SETTINGS.sync()


def createLayout(l: type, parent: Optional[QWidget] = None):
    layout = l(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.setSizeConstraint(QLayout.SetNoConstraint)
    return layout


SPLITTER_HANDLE_WIDTH = 7


class SplitterHandle(QSplitterHandle):
    """ Handle that tells the rest of the interface when a drag starts and ends """

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.LeftButton:
            Database.ON_SPLITTER_DRAG.setValue(True)

    def mouseReleaseEvent(self, event):
        super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            Database.ON_SPLITTER_DRAG.setValue(False)
            self.splitter().saveSizes()


class SplitterGraphics(QSplitter):
    def __init__(self, parent: QWidget, name: str, orientation: Qt.Orientation = Qt.Horizontal):
        super().__init__(orientation, parent)
        self.setObjectName(name)
        self.setHandleWidth(SPLITTER_HANDLE_WIDTH)
        self.setChildrenCollapsible(False)
        self.setOpaqueResize(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def createHandle(self) -> QSplitterHandle:
        return SplitterHandle(self.orientation(), self)

    def minimumSizeHint(self) -> QSize:
        # QSplitter leaves out its own frame, such as the border set in style.qss: without it the window could get
        # narrower than the panes, which would then cover the outer border.
        frame = self.rect().size() - self.contentsRect().size()
        return super().minimumSizeHint() + frame


class SplitterLogic(SplitterGraphics):
    """ Panes slide smoothly down to their own minimum, without collapsing, and the position is kept in the settings """

    def __init__(self, parent: QWidget, name: str, settings_key: str, orientation: Qt.Orientation = Qt.Horizontal):
        super().__init__(parent, name, orientation)
        self.___settings_key: str = settings_key

    def addPane(self, pane: QWidget, minimum: int, stretch: int = 1):
        """
        Add a pane that the splitter can shrink down to minimum pixels.
        The size hints of the content are ignored, so no inner widget stops the handle before that minimum.
        """
        policy = pane.sizePolicy()
        if self.orientation() == Qt.Horizontal:
            policy.setHorizontalPolicy(QSizePolicy.Ignored)
            pane.setMinimumWidth(minimum)
        else:
            policy.setVerticalPolicy(QSizePolicy.Ignored)
            pane.setMinimumHeight(minimum)
        pane.setSizePolicy(policy)
        self.addWidget(pane)
        self.setStretchFactor(self.indexOf(pane), stretch)

    def restoreSizes(self, ratios: list[int]):
        """ Restore the position stored by the user, or split the space by the ratios """
        state = Settings.get(self.___settings_key, None)
        if isinstance(state, QByteArray) and self.restoreState(state):
            self.setChildrenCollapsible(False)
            return
        total = 1_000_000
        self.setSizes([total * ratio // sum(ratios) for ratio in ratios])

    def saveSizes(self):
        """ Store the position. Called on release: at every mouse move it would rewrite the whole INI file """
        Settings.silentSet(self.___settings_key, self.saveState())


class Splitter(SplitterLogic):
    def __init__(self, parent: QWidget, name: str, settings_key: str, orientation: Qt.Orientation = Qt.Horizontal):
        super().__init__(parent, name, settings_key, orientation)


def handleZoomEvent(widget: QWidget, event, zoom_by: callable, reset: callable) -> bool:
    """Handle zoom keys, Ctrl/Cmd + wheel, and pinch gestures. Return True if the event was used."""
    kind = event.type()
    if kind == QEvent.KeyPress:
        # Qt maps the Command key to ControlModifier on macOS.
        modifiers = event.modifiers() & ~Qt.KeypadModifier
        key = event.key()
        if key in (Qt.Key_Plus, Qt.Key_Equal) and (modifiers & ~Qt.ShiftModifier) == Qt.ControlModifier:
            zoom_by(1)
        elif key == Qt.Key_Minus and modifiers == Qt.ControlModifier:
            zoom_by(-1)
        elif key == Qt.Key_0 and modifiers == Qt.ControlModifier:
            reset()
        else:
            return False
    elif kind == QEvent.Wheel and event.modifiers() == Qt.ControlModifier:
        phase = event.phase()
        if phase in (Qt.ScrollBegin, Qt.ScrollEnd, Qt.ScrollMomentum):
            widget._zoom_wheel_delta = 0
        if phase not in (Qt.ScrollEnd, Qt.ScrollMomentum):
            widget._zoom_wheel_delta = getattr(widget, "_zoom_wheel_delta", 0) + event.angleDelta().y()
            steps = int(widget._zoom_wheel_delta / 120)
            if steps:
                widget._zoom_wheel_delta -= steps * 120
                zoom_by(steps)
    elif kind == QEvent.NativeGesture:
        gesture = event.gestureType()
        if gesture in (Qt.BeginNativeGesture, Qt.EndNativeGesture):
            widget._zoom_magnification = 0.0
            return False
        if gesture != Qt.ZoomNativeGesture:
            return False
        widget._zoom_magnification = getattr(widget, "_zoom_magnification", 0.0) + event.value()
        steps = int(widget._zoom_magnification * 10)
        if steps:
            widget._zoom_magnification -= steps / 10
            zoom_by(steps)
    else:
        return False
    event.accept()
    return True


