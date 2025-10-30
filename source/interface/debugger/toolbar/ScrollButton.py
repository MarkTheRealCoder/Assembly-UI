from typing import Literal

from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.templates import GenericButton
from source.interface.templates import Tooltip


class ScrollButtonGraphics(GenericButton):
    def __init__(self, parent, direction: Literal["up", "down"]):
        super().__init__(parent)
        self.setObjectName("ScrollButton")
        # Additional UI setup can be done here
        icon = QIcon(find_path(f"scroll-{direction}.svg"))
        self.setIcon(self.rerenderIcon(icon, "#569CD6"))
        self.setIconSize(QSize(15, 15))

        self.tooltip = Tooltip(self, f"Scroll {direction} the terminal view.")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)


class ScrollButtonLogic(ScrollButtonGraphics):
    def __init__(self, parent, direction: Literal["up", "down"]):
        super().__init__(parent, direction)
        # Implementation of scroll button logic goes here


class ScrollButton(ScrollButtonLogic):
    def __init__(self, parent, direction: Literal["up", "down"]):
        super().__init__(parent, direction)
        # Additional initialization for ScrollButton