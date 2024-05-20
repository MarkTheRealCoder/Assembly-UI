from PyQt5.QtCore import QObject, QPoint, QSize, QEvent
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

from src.eventhandlers.Register import EventRegister
from src.eventhandlers.resize.Controller import Controller
from src.events.data.ClosingEvent import ClosingEvent
from src.events.graphic.CursorChangeEvent import CursorChangeEvent
from src.events.graphic.ResizeEvent import ResizeEvent


class Resizer(QObject):
    def __init__(self, window: QWidget, subset: str):
        super().__init__()

        # Data
        self.___window: QWidget = window

        self.___min_width: int = window.minimumWidth()
        self.___min_height: int = window.minimumHeight()

        # Top Left corner
        self.___tl_x: int = 0
        self.___tl_y: int = 0
        self.___tl_corner: QPoint = QPoint(0, 0)

        # Bottom Right corner
        self.___br_x: int = self.___min_width
        self.___br_y: int = self.___min_height
        self.___br_corner: QPoint = QPoint(self.___min_width, self.___min_height)

        # Miscellaneous
        self.___mouse_pressed: bool = False
        self.___controller = Controller(window, subset)
        self.___subset = subset

        # Configs
        self.configurations()

    def configurations(self):
        self.___window.installEventFilter(self)
        self.___window.mousePressEvent = self.mousePressEvent
        self.___window.mouseReleaseEvent = self.mouseReleaseEvent

        EventRegister.mregister(self.___window, CursorChangeEvent, self.___subset)
        EventRegister.mregister(self.___window, ResizeEvent, self.___subset)

    def mouseReleaseEvent(self, event):
        self.___controller.set_resizable(False)

    def mousePressEvent(self, event):
        self.___controller.set_resizable(True)

    def eventFilter(self, obj, event: QEvent):
        if event == CursorChangeEvent:
            cursor = event.cursor()
            self.___window.setCursor(QCursor(cursor))

        elif event == ResizeEvent:
            direction = event.direction()
            current_pos: QPoint = event.current_pos()
            self.handle_movement(current_pos, direction)

        elif event == ClosingEvent:
            self.___controller.closing()

        elif event.type() == QEvent.FocusIn:
            Controller.set_focused(self.___subset)

        return super().eventFilter(obj, event)

    def handle_movement(self, curr_pos: QPoint, direction: str):
        steps: dict[str: bool] = {}

        for i in direction:
            if i == "N":
                steps["height"] = True
                steps["y"] = True
            elif i == "W":
                steps["width"] = True
                steps["x"] = True
            elif i == "S":
                steps["height"] = True
            elif i == "E":
                steps["width"] = True

        self.step(curr_pos, **steps)

    def step(self, curr_pos: QPoint, **kwargs):
        if len(kwargs) == 0:
            return

        size: QSize = self.___window.size()
        min_width, min_height = self.___min_width, self.___min_height

        window_corner: QPoint = self.___window.pos()
        x, y = window_corner.x(), window_corner.y()

        cx, cy = curr_pos.x(), curr_pos.y()

        width, height = size.width(), size.height()

        do_y = kwargs.get("y", False)
        do_x = kwargs.get("x", False)

        if kwargs.get("height", False):
            _difference = cy - (y if do_y else y + height)
            tmpy = y
            if do_y:
                tmpy += _difference
                _difference = -_difference
            height += _difference
            if height < min_height:
                height = min_height
            else:
                y = tmpy

        if kwargs.get("width", False):
            _difference = cx - (x if do_x else x + width)
            tmpx = x
            if do_x:
                tmpx += _difference
                _difference = -_difference
            width += _difference
            if width < min_width:
                width = min_width
            else:
                x = tmpx

        self.___window.move(x, y)
        self.___window.resize(width, height)