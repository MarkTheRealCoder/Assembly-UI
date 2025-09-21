from PyQt5.QtCore import QSize
from PyQt5.QtGui import QMouseEvent, QIcon

from source.comms.Signals import Variable
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem.Folder import find_path
from source.interface.templates import GenericButton


class CloseButtonGraphics(GenericButton):
    def __init__(self, parent, properties: dict[str, bool] = {}):
        super().__init__(parent)

        icon_size: tuple[int, int] = (20, 20)
        self.setFixedHeight(34)
        if "tab" in properties.keys():
            self.setFixedWidth(34)
            icon_size = (10, 10)

        self.setIconSize(QSize(*icon_size))
        self.setIcon(QIcon(find_path("close.svg")))

        for k, v in properties.items():
            self.setProperty(k, v)


class CloseButtonLogic(CloseButtonGraphics):
    def __init__(self, parent, properties: dict[str, bool] = {}):
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
    def __init__(self, parent, subclass: str = "Main", properties: dict[str, bool] = {}):
        super().__init__(parent, properties)
        self.___subclass: str = subclass
        self.setObjectName("Close")

    def mousePressEvent(self, e: QMouseEvent):
        e.accept()
        EventRegister.send(ClosingEvent(*self.getArgs()), self.___subclass, **self.getIden())
