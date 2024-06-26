from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QLabel, QWidget

from src.graphics.components.memory.GenericSegment import ScrollWidget
from src.tools.ClassMapping import register
from src.tools.Variables import DataBase as db


@register("STACK")
class Stack(ScrollWidget):
    def __init__(self, parent: QWidget, clipboard: QClipboard):
        super().__init__(parent, clipboard, "Stack")
        db.METHOD.connect(self.changeContext)

    def changeContext(self):
        content = db.METHOD.getValue()
        label: QLabel = self.parent().getLabel()
        if content != "":
            label.setText(f"{self.getTitle()} - {content}")
        else:
            label.setText(self.getTitle())
        label.update()
