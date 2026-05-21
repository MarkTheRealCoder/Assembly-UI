from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from source.comms.events import FindShortcutEvent
from source.comms.handlers import EventRegister
from source.filesystem import find_path
from source.interface.templates import GenericButton
from source.interface.templates import Tooltip


class FindButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("FakeFindButton")
        self.show_icon = self.rerenderIcon(QIcon(find_path("search-find.svg")), "#569CD6")
        #self.hide_icon = self.rerenderIcon(QIcon(find_path("close.svg")), "#DA3633")
        # Additional UI setup can be done here
        self.setIcon(self.show_icon)
        self.setIconSize(QSize(16, 16))

        self.tooltip = Tooltip(self, "Search inside the terminal.")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

    def activeProtocol(self):
        self.setProperty("findActive", True)
        self.style().unpolish(self)
        self.style().polish(self)

    def inactiveProtocol(self):
        self.setProperty("findActive", False)
        self.style().unpolish(self)
        self.style().polish(self)


class FindButtonLogic(FindButtonGraphics):
    def __init__(self, parent):
        super().__init__(parent)


@EventRegister.register(FindShortcutEvent, "terminal")
class FindButton(FindButtonLogic):
    def __init__(self, parent):
        super().__init__(parent)
        self.___active = False

    def onFindShortcutEvent(self, event: FindShortcutEvent):
        self.___active = not event.mustClose()
        if self.___active:
            self.activeProtocol()
        else:
            self.inactiveProtocol()