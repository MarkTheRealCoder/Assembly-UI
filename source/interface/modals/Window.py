from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.interface.shared import createLayout
from source.interface.templates import CloseButton
from source.interface.templates import Title
from source.interface.templates.window import BaseWindow
from source.platform import Desktop, isLinux

WINDOWS = []


def createSubWindow(reason: str, parent, wclass, *args, **kwargs):
    global WINDOWS
    if any(map(lambda w: w.reason() == reason, WINDOWS)):
        dup = list(filter(lambda w: w.reason() == reason, WINDOWS))[0]
        WINDOWS.remove(dup)
        EventRegister.send(ClosingEvent(), reason)
    window = Window(reason, parent, wclass, *args, **kwargs)
    WINDOWS.append(window)
    window.show()


def create_window_content(window: BaseWindow) -> QWidget:
    content = QWidget(window)
    container = content
    if isLinux():
        from source.interface.templates.window.base_linux import LinuxResizeFrame

        window.setProperty("linuxFrame", True)
        window.setAttribute(Qt.WA_TranslucentBackground)
        container = LinuxResizeFrame(window, content)
    createLayout(QVBoxLayout, window).addWidget(container)
    return content


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

        tlayout.addWidget(Title(self))
        tlayout.addWidget(CloseButton(self, self._reason))

        tlayout.setStretch(0, 5)
        tlayout.setStretch(1, 1)

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
        screen_geometry = Desktop.getDesktopSize()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


class WindowLogic(WindowGraphics):
    def __init__(self, reason: str, parent, content, *args, **kwargs):
        super().__init__(reason, parent, content, *args, **kwargs)

    def reason(self):
        return self._reason


@EventRegister.register(ClosingEvent, priority=EventRegister.HIGH)
class Window(WindowLogic):
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


