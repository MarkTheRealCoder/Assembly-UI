from PyQt5.QtCore import QEvent

from src.events.Event import Event


class TabAddedEvent(Event):

    ID = QEvent.registerEventType()

    def __init__(self):
        super().__init__(TabAddedEvent.ID)

    @staticmethod
    def gtype():
        return TabAddedEvent.ID