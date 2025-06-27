from PyQt5.QtCore import QEvent

from source.comms.events.Event import Event


class TabListScrollEvent(Event):

    ID = QEvent.registerEventType()

    def __init__(self):
        super().__init__(self.ID)

    @staticmethod
    def gtype():
        return TabListScrollEvent.ID
