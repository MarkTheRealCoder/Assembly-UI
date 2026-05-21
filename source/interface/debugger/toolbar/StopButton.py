from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.templates import GenericButton
from source.interface.templates import Tooltip


class StopButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("StopButton")
        self.setIcon(self.rerenderIcon(QIcon(find_path("stop.svg")), "#FFFFFF"))
        self.setIconSize(QSize(16, 16))
        self.setVisible(False)

        self.tooltip = Tooltip(self, "Stop current execution.")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

    def enable(self):
        self.setVisible(True)

    def disable(self):
        self.setVisible(False)


class StopButtonLogic(StopButtonGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of stop button logic goes here

class StopButton(StopButtonLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for StopButton



