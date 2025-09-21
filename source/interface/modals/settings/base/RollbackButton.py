from typing import Callable

from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.shared import colorize_svg
from source.interface.templates import GenericButton


class RollbackButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(QIcon(colorize_svg(find_path("undo.svg"), "#FFFFFF", (16, 16))))
        self.setObjectName("ResetButton")


class RollbackButtonLogic(RollbackButtonGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self.___function = lambda: None

    def setFunction(self, function: Callable, *args, **kwargs):
        if not callable(function):
            raise ValueError("The provided function is not callable.")

        def wrapper():
            return function(*args, **kwargs)

        self.___function = wrapper
        self.clicked.connect(self.___function)


class RollbackButton(RollbackButtonLogic):
    def __init__(self, parent):
        super().__init__(parent)

