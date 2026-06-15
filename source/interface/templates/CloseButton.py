from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy

from source.comms.Signals import Variable
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem.Folder import find_path
from source.interface.templates import GenericButton


class CloseButtonGraphics(GenericButton):
    def __init__(self, parent, properties: dict[str, bool] = None):
        super().__init__(parent)


        if not properties or "tab" not in properties.keys():
            self.setFixedHeight(34)
            icon_size: tuple[int, int] = (20, 20)
        else:
            icon_size = (10, 10)

        self.setIconSize(QSize(*icon_size))
        self.setIcon(self.rerenderIcon(QIcon(find_path("close.svg")), "#569CD6"))
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        if properties:
            for k, v in properties.items():
                self.setProperty(k, v)


class CloseButtonLogic(CloseButtonGraphics):
    def __init__(self, parent, properties: dict[str, bool] = None):
        super().__init__(parent, properties=properties)
        self.___args = ()
        self.___iden = {}
        self.___signals: list[Variable] = []

    def setEventArgs(self, *args):
        self.___args = args
        return self

    def setEventIdentifiers(self, **iden):
        self.___iden = iden
        return self

    def getArgs(self):
        return self.___args

    def getIden(self):
        return self.___iden


class CloseButton(CloseButtonLogic):
    def __init__(self, parent, subclass: str = "Main", properties: dict[str, bool] = None):
        super().__init__(parent, properties)
        self.___subclass: str = subclass
        self.setObjectName("Close")
        self.clicked.connect(self._onClick)

    def _onClick(self):
        QTimer.singleShot(10, lambda: EventRegister.send(
            ClosingEvent(*self.getArgs()), self.___subclass, **self.getIden()
        ))

