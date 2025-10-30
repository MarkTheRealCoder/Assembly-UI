from PyQt5.QtCore import QEvent

from source.comms.events import Event


class StopEvent(Event):

    Ready = QEvent.registerEventType()

    def __init__(self):
        super().__init__(StopEvent.Ready)

    @staticmethod
    def gtype():
        return StopEvent.Ready