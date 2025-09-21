from typing import Any

from PyQt5.QtCore import pyqtSignal, QObject


class Variable(QObject):
    signal = pyqtSignal(str)

    def __init__(self, _type: type, wrapped: bool = False):
        super(QObject, self).__init__()
        self.___wrapped: bool = wrapped
        if not isinstance(_type, type):
            raise TypeError("_type must be a class not an instance...")
        self.___noneable: bool = False
        self.___type = _type
        self.___value: _type = None
        try:
            self.___value = _type()
        except Exception:
            self.___noneable = True

    def connect(self, func: callable) -> None:
        if not callable(func):
            raise TypeError("Function must be callable...")
        self.signal.connect(func)

    def setValue(self, v: Any) -> None:
        if not isinstance(v, self.___type) and not (v is None and self.___noneable):
            raise TypeError("Type mismatch occurred...")
        self.___value = v
        self.signal.emit(str(v) if v is not None else "None")

    def isEqual(self, v: Any) -> bool:
        if not isinstance(v, self.___type):
            return False
        return self.___value == v

    def getValue(self) -> Any:
        return self.___value

    def getType(self) -> type:
        return self.___type


class DataBase:

    # Decorations
    METHOD: Variable = Variable(str)                        # ON METHOD CHANGE IJVM ONLY

    # Tabs
    ON_TAB_CLOSE: Variable = Variable(int)                  # ON TAB CLOSE
    ON_TAB_SELECTED: Variable = Variable(int)               # ON TAB SELECTED
    ON_TAB_SCROLL: Variable = Variable(bool)                # ON TAB SCROLL

    # Global events
    #ON_SPLITTER_MOVE: Variable = Variable(bool)             # ON SPLITTER MOVE

