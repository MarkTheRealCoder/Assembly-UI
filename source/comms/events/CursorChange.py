from PyQt5.QtCore import QEvent, Qt

from source.comms.events.Event import Event


class CursorChangeEvent(Event):
    CursorChange = QEvent.registerEventType()

    def __init__(self, combination: str):
        super().__init__(self.CursorChange)
        self.___cursor: dict[str: int] = {
            "N": Qt.SizeVerCursor,
            "S": Qt.SizeVerCursor,
            "W": Qt.SizeHorCursor,
            "E": Qt.SizeHorCursor,
            "NW": Qt.SizeFDiagCursor,
            "SE": Qt.SizeFDiagCursor,
            "SW": Qt.SizeBDiagCursor,
            "NE": Qt.SizeBDiagCursor
        }

        self.___cursor_shape: Qt.CursorShape = self.___cursor.get(combination, Qt.ArrowCursor)

    def cursor(self):
        return self.___cursor_shape

    def disabled(self):
        return self.___cursor_shape == Qt.ArrowCursor

    @staticmethod
    def gtype():
        return CursorChangeEvent.CursorChange

