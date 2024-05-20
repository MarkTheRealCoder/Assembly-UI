from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDesktopWidget, QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy, QLabel

from src.eventhandlers.Register import EventRegister
from src.eventhandlers.resize.Resizer import Resizer
from src.events.data.ClosingEvent import ClosingEvent
from src.interface.commons.Commons import createLayout
from src.interface.commons.globals.CloseButton import CloseButton
from src.interface.commons.globals.TopFrame import TopFrame
from src.platform.Adaptability import Desktop

WINDOW_ACTIVE = None


def wOpen(parent, anywidget, title: str, size: QSize = None):
    global WINDOW_ACTIVE
    if WINDOW_ACTIVE is None:
        size = size if size is not None else Desktop.sizeHint(2/5, 3/5)
        WINDOW_ACTIVE = ToolWindow(parent, anywidget, size, title)
        WINDOW_ACTIVE.show()


@EventRegister.register(ClosingEvent, "Tool", EventRegister.LOW)
class ToolWindow(QLabel):

    def __init__(self, parent, widget, size: QSize, title: str):
        super().__init__(parent)
        self.setObjectName("Trash")
        self.setConfigurations(size)
        self.___widget = widget

        self.setMainWidget(widget, title)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.resizeEventHandler = Resizer(self, "Tool")

    def onClosingEvent(self, e):
        global WINDOW_ACTIVE
        WINDOW_ACTIVE = None
        self.deleteLater()

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

        top = TopFrame(self)
        top.setText(title)
        tlayout.addWidget(top)
        tlayout.addWidget(CloseButton.preset(self, "WINDOW", "Tool", True))

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

