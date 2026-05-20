from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.templates import GenericButton, Tooltip


class TimedExecutionButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(self.rerenderIcon(QIcon(find_path("metronome.svg")), "#1D9E75"))
        self.setIconSize(QSize(20, 20))
        self.setVisible(False)


        self.tooltip = Tooltip(self, "")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

    def enable(self):
        self.setVisible(True)

    def disable(self):
        self.setVisible(False)


class TimedExecutionButtonLogic(TimedExecutionButtonGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self.update_interval()

    def update_interval(self, interval=500):
        self.tooltip.setText(f"""Start automatic execution based on given interval\n\n(current interval {"500 ms" if interval == 500 else f"{interval / 1000} s"}).""")


class TimedExecutionButton(TimedExecutionButtonLogic):
    def __init__(self, parent):
        super().__init__(parent)