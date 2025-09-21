from PyQt5.QtWidgets import QWidget, QHBoxLayout

from source.interface.modals.settings.base import RollbackButton
from source.interface.modals.settings.colors.ColorButton import ColorButton
from source.interface.modals.settings.colors.ColorLabel import ColorLabel
from source.interface.modals.settings.colors.HexCodeColorLine import HexCodeColorLine
from source.interface.shared import createLayout


class ColorPickerGraphics(QWidget):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.setObjectName("ColorPicker")
        self.___label = ColorLabel(self, title)
        self.___color_dialog = ColorButton(self)
        self.___hex_converter = HexCodeColorLine(self)
        self.___undo = RollbackButton(self)
        self.setupAppearance()

    def setupAppearance(self):
        self.setContentsMargins(50, 0, 50, 0)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.addWidget(self.___label, 0)
        layout.addWidget(self.___color_dialog, 0)
        layout.addSpacing(10)
        layout.addWidget(self.___hex_converter, 0)
        layout.addStretch(1)
        layout.addWidget(self.___undo, 0)
        self.setLayout(layout)


class ColorPickerLogic(ColorPickerGraphics):
    def __init__(self, parent, title: str):
        super().__init__(parent, title)


class ColorPicker(ColorPickerLogic):
    def __init__(self, parent, title: str):
        super().__init__(parent, title)


