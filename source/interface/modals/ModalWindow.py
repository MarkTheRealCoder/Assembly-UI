from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDesktopWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.comms.handlers.resize import Resizer
from source.interface.shared import createLayout
from source.interface.templates.CloseButton import CloseButton
from source.interface.templates.Title import Title
from source.platform import Desktop

WINDOW_ACTIVE = None


def modalOpen(parent, anywidget, title: str, size: QSize = None):
    global WINDOW_ACTIVE
    if WINDOW_ACTIVE is None:
        size = size if size is not None else Desktop.sizeHint(2/5, 3/5)
        WINDOW_ACTIVE = ModalWindow(parent, anywidget, size, title)
        WINDOW_ACTIVE.show()



class ModalWindowGraphics(QLabel):

    def __init__(self, parent, widget, size: QSize, title: str):
        super().__init__(parent)
        self.setObjectName("Trash")
        self.setConfigurations(size)
        self.___widget = widget

        self.setMainWidget(widget, title)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def setConfigurations(self, size: QSize):
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumSize(size)
        self.centerOnScreen()

    def setMainWidget(self, widget, title: str):
        widget.setParent(self)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout, self)
        mlayout: QHBoxLayout = createLayout(QHBoxLayout, self)

        top = Title(self)
        top.setText(title)
        tlayout.addWidget(top)
        tlayout.addWidget(CloseButton(self, "Tool"))

        tlayout.setStretch(0, 5)
        tlayout.setStretch(1, 1)

        mlayout.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        mlayout.addWidget(widget)
        mlayout.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        mlayout.setStretch(1, 10)

        layout.addLayout(tlayout)
        layout.addLayout(mlayout)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Fixed, QSizePolicy.Expanding))

        layout.setStretch(1, 1)
        self.setLayout(layout)

    def centerOnScreen(self):
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


class ModalWindow(ModalWindowGraphics):
    def __init__(self, parent, widget, size: QSize, title: str):
        super().__init__(parent, widget, size, title)
        self.resizeEventHandler = Resizer(self, "Tool")
        EventRegister.mregister(self, ClosingEvent, "Tool", EventRegister.LOW)

    def onClosingEvent(self, e):
        print("Closing Tool Window")
        global WINDOW_ACTIVE
        WINDOW_ACTIVE = None
        self.deleteLater()
        self.close()

    def event(self, e):
        return super().event(e)
