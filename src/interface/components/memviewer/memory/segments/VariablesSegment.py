from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QWidget, QLabel

from src.interface.commons.ClassMapper import register
from src.interface.components.memviewer.memory.GenericSegment import ScrollWidget
from src.signals.Variables import DataBase as db


@register("VARIABLES")
class Variables(ScrollWidget):
    def __init__(self, parent: QWidget, clipboard: QClipboard):
        super().__init__(parent, clipboard, "Variables")
        db.METHOD.connect(self.changeContext)

    def changeContext(self):
        content = db.METHOD.getValue()
        label: QLabel = self.parent().getLabel()
        if content != "":
            label.setText(f"Variables - {content}")
        else:
            label.setText(self.getTitle())
        label.update()
