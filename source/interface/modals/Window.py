from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.comms.handlers.resize import Resizer
from source.interface.shared import createLayout
from source.interface.templates import CloseButton
from source.interface.templates import Title
from source.platform import Desktop

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


class WindowGraphics(QLabel):
    def __init__(self, reason: str, parent, content, *args, **kwargs):
        super().__init__(parent)

        self._reason = reason
        self.configurations(content(self, *args, **kwargs))

    def configurations(self, content: QWidget):
        self.defineWindowSize()
        self.setObjectName("Window")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout, self)
        mlayout: QHBoxLayout = createLayout(QHBoxLayout, self)

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
        self.setLayout(layout)

    def defineWindowSize(self):
        self.setMinimumSize(Desktop.sizeHint(2 / 5, 2 / 4))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.centerOnScreen()

    def centerOnScreen(self):
        screen_geometry = Desktop.getDesktopSize()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)



class Window(WindowGraphics):
    def __init__(self, reason: str, parent, content, *args, **kwargs):
        super().__init__(reason, parent, content, *args, **kwargs)

        EventRegister.mregister(self, ClosingEvent, reason, EventRegister.HIGH)

        self.resizeEventHandler = Resizer(self, reason)

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

    def reason(self):
        return self._reason


