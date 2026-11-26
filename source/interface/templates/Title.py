from typing import Literal

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy


class TitleGraphics(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setAlignment(Qt.AlignCenter)
        self.setObjectName("Title")


class TitleLogic(TitleGraphics):
    def __init__(self, parent):
        super().__init__(parent)

        self.___left_double_click = None
        self.___left_ctrl_click = None

    def setActionOn(self, event: Literal["LeftCtrlClick", "LeftDoubleClick"], func):
        """Set the callable to run on a left ctrl-click or a left double click."""
        if not callable(func):
            raise TypeError('Func must be a callable...')
        if event == "LeftDoubleClick":
            self.___left_double_click = func
        elif event == "LeftCtrlClick":
            self.___left_ctrl_click = func

    def leftDoubleClick(self):
        if self.___left_double_click is not None:
            self.___left_double_click()

    def leftCtrlClick(self):
        if self.___left_ctrl_click is not None:
            self.___left_ctrl_click()


class Title(TitleLogic):
    """Title label that moves the window when dragged and runs the actions set for double click and ctrl-click."""

    def __init__(self, parent):
        super().__init__(parent)
        self.installEventFilter(self)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            if e.type() == QEvent.MouseButtonDblClick:
                self.leftDoubleClick()

            elif e.type() == QEvent.MouseButtonPress:
                if e.modifiers() & Qt.ControlModifier:
                    self.leftCtrlClick()
                else:
                    self._move()
        return super().mousePressEvent(e)

    def _move(self):
        window = self.window().windowHandle()
        window.startSystemMove()
