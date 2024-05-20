from threading import Semaphore

from PyQt5.QtCore import QObject
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget

from src.asynctasks.Scheduler import Scheduler
from src.eventhandlers.Register import EventRegister
from src.events.graphic.CursorChangeEvent import CursorChangeEvent
from src.events.graphic.ResizeEvent import ResizeEvent


class Controller(QObject):

    ___ACCEPTABLE_DEVIATION: int = 10
    ___focused: str = "Main"

    def __init__(self, window, subset):
        super().__init__()

        self.___subset: str = subset
        self.___window: QWidget = window

        self.___cmp = QCursor.pos()
        self.___direction: str = ""
        self.___resizable: bool = False

        self.___last_comb: dict[str: bool] = None

        self.___sem: Semaphore = Semaphore(1)

        self.___mouse_update: Scheduler = Scheduler(0.01, self.___update_mouse_position)
        self.___cursor_change: Scheduler = Scheduler(0.01, self.fire_cursor_change_event)
        self.___resize: Scheduler = Scheduler(0.01, self.___resize_window)

    def closing(self):
        self.___mouse_update.terminate()
        self.___cursor_change.terminate()
        self.___resize.terminate()

    def ___update_mouse_position(self):
        if Controller.___focused != self.___subset:
            return
        self.___sem.acquire()
        self.___lmp = self.___cmp
        self.___cmp = QCursor.pos()
        self.___sem.release()

    def ___combinations(self):
        ad = Controller.___ACCEPTABLE_DEVIATION
        x = self.___window.width()
        y = self.___window.height()
        pos = self.___window.mapFromGlobal(self.___cmp)

        combinations: dict[str: bool] = {
            "N": 0 <= pos.y() <= ad,
            "S": y >= pos.y() >= y - ad,
            "W": 0 <= pos.x() <= ad,
            "E": x >= pos.x() >= x - ad
        }
        return combinations

    def fire_cursor_change_event(self):
        if Controller.___focused != self.___subset or self.___resizable:
            return
        self.___sem.acquire()
        combinations = self.___combinations()
        if combinations != self.___last_comb:
            self.___direction = "".join([i for i in combinations.keys() if combinations[i]])
            EventRegister.post(CursorChangeEvent, self.___direction, arg=self.___subset)
        self.___last_comb = combinations
        self.___sem.release()

    def ___resize_window(self):
        if not self.___resizable:
            return
        EventRegister.post(ResizeEvent, self.___cmp, self.___direction, arg=self.___subset)

    def set_resizable(self, resizable: bool):
        self.___resizable = resizable

    @staticmethod
    def set_focused(focused: str):
        Controller.___focused = focused



