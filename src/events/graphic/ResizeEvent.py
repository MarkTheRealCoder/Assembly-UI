from PyQt5.QtCore import QPoint, QEvent

from src.events.Event import Event


class ResizeEvent(Event):

    ID = QEvent.registerEventType()

    def __init__(self, cmp: QPoint, direction: str):
        super().__init__(self.ID)

        self.___cmp: QPoint = cmp
        self.___direction: str = direction

    def current_pos(self):
        return self.___cmp

    def direction(self):
        return self.___direction

    @staticmethod
    def gtype():
        return ResizeEvent.ID

