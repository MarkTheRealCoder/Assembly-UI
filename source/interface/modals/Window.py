from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.interface.shared import createLayout
from source.interface.templates import CloseButton
from source.interface.templates import Title
from source.interface.templates.window import BaseWindow
from source.platform import Desktop, isLinux, isMac

WINDOWS = []
MAC_CONTROLS_WIDTH = 38
MAC_CONTROLS_HEIGHT = 34


def createSubWindow(reason: str, parent, wclass, *args, **kwargs):
    """Open a sub window, first closing any open one with the same reason."""
    global WINDOWS
    if any(map(lambda w: w.reason() == reason, WINDOWS)):
        dup = list(filter(lambda w: w.reason() == reason, WINDOWS))[0]
        WINDOWS.remove(dup)
        EventRegister.send(ClosingEvent(), reason)
    window = Window(reason, parent, wclass, *args, **kwargs)
    WINDOWS.append(window)
    window.show()


def create_window_content(window: BaseWindow) -> QWidget:
    """Create the content widget of a window, wrapped in a ResizeFrame on Linux and macOS."""
    content = QWidget(window)
    container = content
    if isLinux() or isMac():
        from source.interface.templates.window.base_linux import ResizeFrame

        window.setProperty("linuxFrame" if isLinux() else "macFrame", True)
        window.setAttribute(Qt.WA_TranslucentBackground)
        container = ResizeFrame(window, content)
    createLayout(QVBoxLayout, window).addWidget(container)
    return content


def add_title_controls(window: BaseWindow, layout: QHBoxLayout, title: QWidget, subclass: str):
    """Add the title and the close button to the layout, with the close control on the left on macOS."""
    if not isMac():
        layout.addWidget(title)
        layout.addWidget(CloseButton(window, subclass))
        layout.setStretch(0, 5)
        layout.setStretch(1, 1)
        return

    controls = QWidget(window)
    controls.setObjectName("WindowControls")
    controls.setProperty("platform", "mac")
    controls.setFixedSize(MAC_CONTROLS_WIDTH, MAC_CONTROLS_HEIGHT)
    controls_layout: QHBoxLayout = createLayout(QHBoxLayout, controls)
    controls_layout.setContentsMargins(12, 0, 12, 0)
    close = CloseButton(controls, subclass, properties={"mac": True, "standalone": True})
    close.setIconSize(QSize(0, 0))
    controls_layout.addWidget(close, alignment=Qt.AlignVCenter)

    layout.addWidget(controls)
    layout.addWidget(title, 1)
    # The spacer keeps the title centered on the window.
    layout.addSpacerItem(QSpacerItem(MAC_CONTROLS_WIDTH, 0, QSizePolicy.Fixed, QSizePolicy.Minimum))


class WindowGraphics(BaseWindow):
    def __init__(self, reason: str, parent, content, *args, **kwargs):
        super().__init__(parent)
        self.setFrameless(["close"], flags=[Qt.Tool])
        self._reason = reason
        self.defineWindowSize()
        self.configurations(content(self, *args, **kwargs))

    def configurations(self, content: QWidget):
        self.setObjectName("Window")
        widget = create_window_content(self)
        layout: QVBoxLayout = createLayout(QVBoxLayout, widget)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout)
        mlayout: QHBoxLayout = createLayout(QHBoxLayout)

        add_title_controls(self, tlayout, Title(self), self._reason)

        mlayout.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        mlayout.addWidget(content)
        mlayout.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        mlayout.setStretch(1, 10)

        layout.addLayout(tlayout)
        layout.addLayout(mlayout)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Fixed, QSizePolicy.Expanding))

        layout.setStretch(1, 1)
        widget.setLayout(layout)

    def defineWindowSize(self):
        self.setMinimumSize(Desktop.sizeHint(2 / 5, 2 / 4))
        self.centerOnScreen()

    def centerOnScreen(self):
        Desktop.centerWidget(self, self.parentWidget())


class WindowLogic(WindowGraphics):
    def __init__(self, reason: str, parent, content, *args, **kwargs):
        super().__init__(reason, parent, content, *args, **kwargs)

    def reason(self):
        return self._reason


@EventRegister.register(ClosingEvent, priority=EventRegister.HIGH)
class Window(WindowLogic):
    """Frameless tool window that hosts a content widget and closes on the ClosingEvent of its reason."""
    def __init__(self, reason: str, parent, content, *args, **kwargs):
        super().__init__(reason, parent, content, *args, **kwargs)
        EventRegister.mregister(self, ClosingEvent, reason, EventRegister.HIGH)

    def onClosingEvent(self, event):
        try:
            global WINDOWS
            WINDOWS.remove(self)
        except ValueError:
            pass
        self.close()
        self.deleteLater()

    def focusInEvent(self, event):
        self.eventFilter(self, event)
        return super().focusInEvent(event)

    def event(self, e):
        return super().event(e)


