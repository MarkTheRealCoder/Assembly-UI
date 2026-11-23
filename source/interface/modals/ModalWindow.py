from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QSpacerItem, QSizePolicy

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.interface.modals.Window import add_title_controls, create_window_content
from source.interface.shared import createLayout
from source.interface.templates import Title
from source.interface.templates.window import BaseWindow
from source.platform import Desktop

WINDOW_ACTIVE = None


def modalOpen(parent, anywidget, title: str, size: QSize = None):
    global WINDOW_ACTIVE
    if WINDOW_ACTIVE is None:
        size = size if size is not None else Desktop.sizeHint(2/5, 3/5)
        WINDOW_ACTIVE = ModalWindow(parent, anywidget, size, title)
        WINDOW_ACTIVE.show()


class ModalWindowGraphics(BaseWindow):
    def __init__(self, parent, widget, size: QSize, title: str):
        super().__init__(parent)
        self.setFrameless(["close"], flags=[Qt.Tool])
        self.setConfigurations(size)
        self.___widget = widget
        self.setMainWidget(widget, title)

    def setConfigurations(self, size: QSize):
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumSize(size)
        self.centerOnScreen()

    def setMainWidget(self, content, title: str):
        self.setObjectName("Trash")
        widget = create_window_content(self)

        layout: QVBoxLayout = createLayout(QVBoxLayout, widget)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout)
        mlayout: QHBoxLayout = createLayout(QHBoxLayout)

        top = Title(self)
        top.setText(title)
        add_title_controls(self, tlayout, top, "Tool")

        mlayout.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))
        mlayout.addWidget(content)
        mlayout.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Expanding, QSizePolicy.Fixed))

        mlayout.setStretch(1, 10)

        layout.addLayout(tlayout)
        layout.addLayout(mlayout)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Fixed, QSizePolicy.Expanding))

        layout.setStretch(1, 1)
        widget.setLayout(layout)

    def centerOnScreen(self):
        Desktop.centerWidget(self, self.parentWidget())


class ModalWindowLogic(ModalWindowGraphics):
    def __init__(self, parent, widget, size: QSize, title: str):
        super().__init__(parent, widget, size, title)

@EventRegister.register(ClosingEvent, "Main")
@EventRegister.register(ClosingEvent, "Tool", EventRegister.LOW)
class ModalWindow(ModalWindowLogic):
    def __init__(self, parent, widget, size: QSize, title: str):
        super().__init__(parent, widget, size, title)

    def onClosingEvent(self, e):
        global WINDOW_ACTIVE
        WINDOW_ACTIVE = None
        self.deleteLater()
        self.close()
