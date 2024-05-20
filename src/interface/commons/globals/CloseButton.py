from typing import Literal

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QMouseEvent, QIcon
from PyQt5.QtWidgets import QPushButton, QSizePolicy

from src.eventhandlers.Register import EventRegister
from src.events.data.ClosingEvent import ClosingEvent
from src.events.graphic.CursorChangeEvent import CursorChangeEvent
from src.filesystem.Folder import find_path
from src.signals.Variables import Variable


class CloseButton(QPushButton):
    def __init__(self, parent, subclass: str = "Main"):
        super().__init__(parent)
        self.___subclass: str = subclass
        self.___args = ()
        self.___iden = {}
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        self.___event_enabled = True
        self.___signals: list[Variable] = []

    def setEventArgs(self, *args):
        self.___args = args
        return self

    def setEventIdentifiers(self, **iden):
        self.___iden = iden
        return self

    def onCursorChangeEvent(self, e: CursorChangeEvent):
        self.___event_enabled = e.disabled()

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        print("Closing", self.___subclass)
        EventRegister.send(ClosingEvent(*self.___args), self.___subclass, **self.___iden)
        e.accept()

    @staticmethod
    def preset(p, btype: Literal["WINDOW", "TAB"], sc: str = "Main", squared: bool = False):
        btn = CloseButton(p, sc)
        if btype == "WINDOW":
            btn.setIcon(QIcon(find_path("close.png")))
            btn.setIconSize(QSize(20, 20))
            btn.setObjectName("Close")
            btn.setFixedHeight(34)
            if squared:
                btn.setFixedWidth(34)
        elif btype == "TAB":
            btn.setIcon(QIcon(find_path("small_close_icon.png")))
            btn.setIconSize(QSize(10, 10))
            btn.setObjectName("TabCloseButton")
            btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        else:
            raise ValueError("Invalid type")
        return btn
