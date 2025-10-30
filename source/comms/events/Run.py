from PyQt5.QtCore import QEvent

from source.comms.events import Event


class RunEvent(Event):

    Ready = QEvent.registerEventType()

    def __init__(self, debug=False):
        super().__init__(RunEvent.Ready)
        self.___debug: bool = debug

    def is_debug(self) -> bool:
        return self.___debug

    @staticmethod
    def gtype():
        return RunEvent.Ready