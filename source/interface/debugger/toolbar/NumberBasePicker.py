from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QComboBox, QStyle, QStyleOptionComboBox, QStylePainter

from source.interface.templates import Tooltip


class NumberBasePickerGraphics(QComboBox):
    # Display bases in menu order: label, base and tooltip name.
    BASES = (("HEX", 16, "hexadecimal"), ("DEC", 10, "decimal"), ("OCT", 8, "octal"))

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("NumberBasePicker")
        for label, base, _ in self.BASES:
            self.addItem(label, base)

        self.tooltip = Tooltip(self, "")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)
        self.updateGraphic()

    def paintEvent(self, event):
        """ Draw the box as usual and the label centered in the whole box, since there is no arrow """
        option = QStyleOptionComboBox()
        self.initStyleOption(option)
        text = option.currentText
        option.currentText = ""
        painter = QStylePainter(self)
        painter.drawComplexControl(QStyle.CC_ComboBox, option)
        painter.setPen(self.palette().color(QPalette.ButtonText))
        painter.drawText(self.rect(), Qt.AlignCenter, text)

    def updateGraphic(self):
        """ Show the active base in the tooltip """
        name = self.BASES[self.currentIndex()][2]
        self.tooltip.setText(f"Memory values in {name}.\nPick the base of the memory values.")


class NumberBasePicker(NumberBasePickerGraphics):
    """ Selector of the base of the memory values: hexadecimal (default), decimal or octal. """
    baseChanged = pyqtSignal(int)

    def __init__(self, parent):
        super().__init__(parent)
        self.currentIndexChanged.connect(self.___onIndexChanged)

    def base(self) -> int:
        return self.currentData()

    def ___onIndexChanged(self, _index: int):
        self.updateGraphic()
        self.baseChanged.emit(self.currentData())
