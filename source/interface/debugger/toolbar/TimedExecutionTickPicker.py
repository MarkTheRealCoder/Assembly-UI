from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QComboBox

from source.filesystem import find_path
from source.interface.templates import Tooltip, GenericButton


class TimedExecutionTickPickerGraphics(QComboBox):
    def __init__(self, parent):
        super().__init__(parent)
        self.setVisible(False)

        self.tooltip = Tooltip(self, "Pick an interval for automatic execution.")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

        for i, t in enumerate([500, 1000, 2000, 3000, 4000, 5000, 10000]):
            self.addItem(f"{t // 1000} s" if t >= 1000 else f"{t} ms", t)
            self.setItemIcon(i, GenericButton.rerenderIcon(QIcon(find_path("clock.svg")), "#888"))

    def enable(self):
        self.setVisible(True)

    def disable(self):
        self.setVisible(False)


class TimedExecutionTickPickerLogic(TimedExecutionTickPickerGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class TimedExecutionTickPicker(TimedExecutionTickPickerLogic):
    def __init__(self, parent):
        super().__init__(parent)

