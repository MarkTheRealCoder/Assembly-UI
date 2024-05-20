from PyQt5.QtCore import QEvent

from src.events.Event import Event


class ReadyEvent(Event):

    Ready = QEvent.registerEventType()

    def __init__(self):
        super().__init__(ReadyEvent.Ready)

    @staticmethod
    def gtype():
        return ReadyEvent.Ready

