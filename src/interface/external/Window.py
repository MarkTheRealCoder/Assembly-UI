from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QSpacerItem, QSizePolicy, QLabel, QApplication

from src.eventhandlers.Register import EventRegister
from src.eventhandlers.resize.Resizer import Resizer
from src.events.data.ClosingEvent import ClosingEvent
from src.interface.commons.Commons import createLayout
from src.interface.commons.globals.CloseButton import CloseButton
from src.interface.commons.globals.TopFrame import TopFrame
from src.platform.Adaptability import Desktop

WINDOWS = []


def createSubWindow(reason: str, parent, wclass, *args, **kwargs):
    global WINDOWS
    window = Window(reason, parent, wclass, *args, **kwargs)
    if any(map(lambda w: w.reason() == reason, WINDOWS)):
        dup = list(filter(lambda w: w.reason() == reason, WINDOWS))[0]
        dup.hide()
        QApplication.instance().postEvent(dup, ClosingEvent())
    WINDOWS.append(window)
    window.show()


@EventRegister.register(ClosingEvent, priority=EventRegister.HIGH)
class Window(QLabel):
    def __init__(self, reason: str, parent, content, *args, **kwargs):
        super().__init__(parent)

        self.___reason = reason
        self.configurations(content(self, *args, **kwargs))
        EventRegister.mregister(self, ClosingEvent, reason, EventRegister.LOW)

        self.resizeEventHandler = Resizer(self, reason)

    def configurations(self, content: QWidget):
        self.defineWindowSize()
        self.setObjectName("Window")
        self.setWindowFlags(Qt.Tool | Qt.FramelessWindowHint)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout, self)
        mlayout: QHBoxLayout = createLayout(QHBoxLayout, self)

        tlayout.addWidget(TopFrame(self))
        tlayout.addWidget(CloseButton.preset(self, "WINDOW", self.___reason, True))

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

    def onClosingEvent(self, event):
        global WINDOWS
        WINDOWS.remove(self)
        self.deleteLater()

    def focusInEvent(self, event):
        self.eventFilter(self, event)
        return super().focusInEvent(event)

    def reason(self):
        return self.___reason



