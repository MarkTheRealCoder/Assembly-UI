from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.templates import GenericButton, Tooltip


class StepButtonGraphics(GenericButton):
    def __init__(self, parent, step_size: int = 1):
        super().__init__(parent)
        icon_path = "step_1.svg" if step_size == 1 else "step_10.svg"
        self.setIcon(self.rerenderIcon(QIcon(find_path(icon_path)), "#1D9E75"))
        self.setIconSize(QSize(20, 20))
        self.setVisible(False)

        self.tooltip = Tooltip(self, f"Step ahead of {step_size} instruction/s.")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

    def enable(self):
        self.setVisible(True)

    def disable(self):
        self.setVisible(False)


class StepButtonLogic(StepButtonGraphics):
    def __init__(self, parent, step_size: int = 1):
        super().__init__(parent, step_size)
        self.__step_size = step_size

    def step_ahead(self):
        print(f"Stepping ahead by {self.__step_size} instruction/s.")


class StepButton(StepButtonLogic):
    def __init__(self, parent, step_size: int = 1):
        super().__init__(parent, step_size)
        self.clicked.connect(self.step_ahead)