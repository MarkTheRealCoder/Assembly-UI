from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.templates import GenericButton
from source.interface.templates import Tooltip


class ClearButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ClearButton")
        # Additional UI setup can be done here
        self.std_icon = self.rerenderIcon(QIcon(find_path("clear.svg")), "#569CD6")
        self.confirmation_icon = self.rerenderIcon(QIcon(find_path("confirm.svg")), "#FFFFFF")
        self.setIcon(self.std_icon)
        self.setIconSize(QSize(15, 15))

        self.tooltip = Tooltip(self, "Clear terminal output.")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

    def reloadStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def activeProtocol(self):
        self.setProperty("active", True)
        self.setIcon(self.confirmation_icon)
        self.reloadStyle()
        self.tooltip.setText("Click again to confirm choice or\nmove cursor away to cancel.")
        self.tooltip.showTooltip()

    def inactiveProtocol(self):
        self.setProperty("active", False)
        self.setIcon(self.std_icon)
        self.reloadStyle()
        self.tooltip.hideTooltip()
        self.tooltip.setText("Clear terminal output.")


class ClearButtonLogic(ClearButtonGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of clear button logic goes here


class ClearButton(ClearButtonLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for ClearButton

    def leaveEvent(self, event):
        self.inactiveProtocol()
        super().leaveEvent(event)