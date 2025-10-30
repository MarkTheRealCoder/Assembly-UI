from PyQt5.QtCore import QEvent

from source.comms.events import Event


class FindShortcutEvent(Event):

    Ready = QEvent.registerEventType()

    def __init__(self):
        super().__init__(FindShortcutEvent.Ready)


    @staticmethod
    def gtype():
        return FindShortcutEvent.Ready