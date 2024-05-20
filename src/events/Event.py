from PyQt5.QtCore import QEvent, QObject


class Event(QEvent):
    def __init__(self, et: QEvent.Type):
        super().__init__(et)
        self.___type = et

    def __ne__(self, other):
        return not self.__eq__(other)

    def __eq__(self, other):
        if isinstance(other, QEvent.Type):
            return self.type() == other
        elif isinstance(other, Event):
            return self.type() == other.type()
        elif isinstance(other, type):
            return self.type() == other.gtype()
        return False

    def on(self, obj: QObject):
        pass

    @staticmethod
    def gtype(): ...


