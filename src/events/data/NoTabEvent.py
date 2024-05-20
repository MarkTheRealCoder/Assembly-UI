from PyQt5.QtCore import QEvent

from src.events.Event import Event


class NoTabEvent(Event):
    NoTab = QEvent.registerEventType()

    def __init__(self):
        super().__init__(NoTabEvent.NoTab)

    @staticmethod
    def gtype():
        return NoTabEvent.NoTab