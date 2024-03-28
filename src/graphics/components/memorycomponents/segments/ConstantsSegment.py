from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QWidget

from src.graphics.components.memorycomponents.GenericSegment import ScrollWidget
from src.tools.ClassMapping import register


@register("CONSTANTS")
class Constants(ScrollWidget):
    def __init__(self, parent: QWidget, clipboard: QClipboard):
        super().__init__(parent, clipboard, "Constants")
