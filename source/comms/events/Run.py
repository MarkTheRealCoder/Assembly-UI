from PyQt5.QtCore import QEvent

from source.comms.events.Event import Event


class RunEvent(Event):

    Ready = QEvent.registerEventType()

    def __init__(self):
        super().__init__(RunEvent.Ready)

    @staticmethod
    def gtype():
        return RunEvent.Ready