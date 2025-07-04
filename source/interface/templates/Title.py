from typing import Literal

from PyQt5.QtCore import QEvent, QObject, Qt, QRect, QPoint
from PyQt5.QtWidgets import QLabel, QSizePolicy, QDesktopWidget, QWidget

from source.comms.events import CursorChangeEvent
from source.comms.handlers import EventRegister


class TitleGraphics(QLabel):

    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.setAlignment(Qt.AlignCenter)


class TitleLogic(TitleGraphics):
    def __init__(self, parent, mw: QWidget = None):
        super().__init__(parent)
        self.mw: QWidget = mw if mw is not None else parent

        self.___left_double_click = None
        self.___left_ctrl_click = None

        self.__mousePressPos = 0
        self.__mouseMovePos = 0

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

    def setMovePosition(self, pos: QPoint):
        self.__mouseMovePos = pos

    def setPressPosition(self, pos: QPoint):
        self.__mousePressPos = pos

    def leftDoubleClick(self):
        if self.___left_double_click is not None:
            self.___left_double_click()

    def leftCtrlClick(self):
        if self.___left_ctrl_click is not None:
            self.___left_ctrl_click()


@EventRegister.register(CursorChangeEvent, "Main", EventRegister.HIGH)
class Title(TitleLogic):
    movable: bool = False

    def __init__(self, parent, mw: QWidget = None):
        super().__init__(parent, mw)
        self.___event_enabled = True

        self.installEventFilter(self)
        self.setObjectName("Title")

    def onCursorChangeEvent(self, e: CursorChangeEvent):
        self.___event_enabled = e.disabled()

    def eventFilter(self, o: QObject, e: QEvent) -> bool:

        if not self.___event_enabled:
            return super().eventFilter(o, e)

        if e.type() == QEvent.MouseMove and Title.movable:
            self.moveWindow(e)

        elif hasattr(e, "button") and e.button() == Qt.LeftButton:

            if e.type() == QEvent.MouseButtonDblClick:
                self.leftDoubleClick()

            elif e.type() == QEvent.MouseButtonPress:

                if e.modifiers() & Qt.ControlModifier:
                    self.leftCtrlClick()
                else:
                    Title.movable = True  # e.pos().y() > 10
                    self.setPressPosition(e.globalPos())
                    self.setMovePosition(e.globalPos())

            elif e.type() == QEvent.MouseButtonRelease:
                Title.movable = False

        return super().eventFilter(o, e)



