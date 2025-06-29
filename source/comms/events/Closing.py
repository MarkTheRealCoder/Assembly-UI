from PyQt5.QtCore import QEvent, QObject

from source.comms.events.Event import Event


class ClosingEvent(Event):

    Closing = QEvent.registerEventType()

    def __init__(self, *args):
        super().__init__(ClosingEvent.Closing)
        self.___args = args

    def on(self, obj: QObject):
        from source.comms.handlers import EventRegister
        EventRegister.remove(obj)

    def args(self):
        return self.___args

    @staticmethod
    def gtype():
        return ClosingEvent.Closing
