from typing import Literal

from PyQt5.QtCore import QEvent, QObject, Qt, QRect, QPoint
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QLabel, QMainWindow, QSizePolicy, QDesktopWidget, QWidget

from src.tools.Tools import open_dir
from src.tools.Variables import DataBase as db


class TopFrame(QLabel):
    movable: bool = False

    def __init__(self, parent, mw: QWidget = None):
        super().__init__(parent)
        self.mw: QWidget = mw if mw is not None else parent

        self.___left_double_click = None
        self.___left_ctrl_click = None

        self.__mousePressPos = 0
        self.__mouseMovePos = 0
        self.setObjectName("TopFrame")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)

        self.installEventFilter(self)
        self.___event_enabled = True

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if not self.___event_enabled:
            return super().eventFilter(o, e)

        if e.type() == QEvent.MouseMove and TopFrame.movable:
            self.moveWindow(e)

        elif hasattr(e, "button") and e.button() == Qt.LeftButton:

            if e.type() == QEvent.MouseButtonDblClick:
                if self.___left_double_click is not None:
                    self.___left_double_click()

            elif e.type() == QEvent.MouseButtonPress:

                if e.modifiers() & Qt.ControlModifier:
                    if self.___left_ctrl_click is not None:
                        self.___left_ctrl_click()
                else:
                    TopFrame.movable = True  # e.pos().y() > 10
                    self.__mousePressPos = e.globalPos()
                    self.__mouseMovePos = e.globalPos()

            elif e.type() == QEvent.MouseButtonRelease:
                TopFrame.movable = False

        return super().eventFilter(o, e)

    def moveWindow(self, e: QEvent):
        desk = QDesktopWidget()
        screen_rect: QRect = desk.availableGeometry()
        del desk
        bottom_right: QPoint = screen_rect.bottomRight()
        global_pos = e.globalPos()
        diff = global_pos - self.__mouseMovePos
        self.__mouseMovePos = global_pos
        curr_pos: QPoint = self.mw.pos()
        if (curr_pos.y() + diff.y()) < bottom_right.y() - 15:
            self.mw.move(curr_pos + diff)

    def setActionOn(self, event: Literal["LeftCtrlClick", "LeftDoubleClick"], func):
        if not callable(func):
            raise TypeError('Func must be a callable...')
        if event == "LeftDoubleClick":
            self.___left_double_click = func
        elif event == "LeftCtrlClick":
            self.___left_ctrl_click = func
