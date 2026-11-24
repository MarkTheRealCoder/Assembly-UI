from PyQt5.QtCore import pyqtSignal

from source.interface.templates import GenericButton, Tooltip


class NumberBaseButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("NumberBaseButton")
        self.setCheckable(True)
        self.setChecked(True)
        self.setText("HEX")

        self.tooltip = Tooltip(self, "")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)
        self.updateGraphic()

    def updateGraphic(self):
        """ Show the active base and the base that a click selects """
        hexadecimal = self.isChecked()
        self.setText("HEX" if hexadecimal else "DEC")
        self.tooltip.setText(f"Memory values in {'hexadecimal' if hexadecimal else 'decimal'}.\n"
                             f"Click to show them in {'decimal' if hexadecimal else 'hexadecimal'}.")


class NumberBaseButton(NumberBaseButtonGraphics):
    """ Toggle between hexadecimal and decimal memory values. Hexadecimal is the default. """
    baseChanged = pyqtSignal(bool)

    def __init__(self, parent):
        super().__init__(parent)
        self.toggled.connect(self.___onToggled)

    def isHexadecimal(self) -> bool:
        return self.isChecked()

    def ___onToggled(self, checked: bool):
        self.updateGraphic()
        self.baseChanged.emit(checked)
