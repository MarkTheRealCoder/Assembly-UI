from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.templates import GenericButton
from source.interface.templates import Tooltip


class RunButtonGraphics(GenericButton):
    def __init__(self, parent, icon_path):
        super().__init__(parent)
        self.setObjectName("RunButton")
        # Additional UI setup can be done here
        self.not_active = self.rerenderIcon(QIcon(find_path(icon_path)), "#3FB950")
        self.active = self.rerenderIcon(QIcon(find_path(icon_path)), "#FFFFFF")
        self.setIcon(self.not_active)
        self.setIconSize(QSize(15, 15))

        self.tooltip = Tooltip(self, "Run current program.")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

    def reloadStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def activeProtocol(self):
        self.setProperty("active", True)
        self.setIcon(self.active)
        self.reloadStyle()

    def inactiveProtocol(self):
        self.setProperty("active", False)
        self.setIcon(self.not_active)
        self.reloadStyle()


class RunButtonLogic(RunButtonGraphics):
    def __init__(self, parent, icon_path):
        super().__init__(parent, icon_path)
        # Implementation of run button logic goes here

    def disable(self):
        self.setDisabled(True)

    def enable(self):
        self.setDisabled(False)


class RunButton(RunButtonLogic):
    def __init__(self, parent, icon_path="run.svg"):
        super().__init__(parent, icon_path)
        # Additional initialization for RunButton