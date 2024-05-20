from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QWidget

from src.interface.commons.ClassMapper import register
from src.interface.components.memviewer.memory.GenericSegment import ScrollWidget


@register("CONSTANTS")
class Constants(ScrollWidget):
    def __init__(self, parent: QWidget, clipboard: QClipboard):
        super().__init__(parent, clipboard, "Constants")
