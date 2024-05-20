from PyQt5.QtCore import QEvent

from src.events.Event import Event


class TabListScrollEvent(Event):

    ID = QEvent.registerEventType()

    def __init__(self):
        super().__init__(self.ID)

    @staticmethod
    def gtype():
        return TabListScrollEvent.ID
