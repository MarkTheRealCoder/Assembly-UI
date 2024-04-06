from typing import Any

from PyQt5.QtCore import pyqtSignal, QObject


class Variable(QObject):
    signal = pyqtSignal(str)

    def __init__(self, _type: type):
        super(QObject, self).__init__()
        if not isinstance(_type, type):
            raise TypeError("_type must be a class not an instance...")
        self.___type = _type
        self.___value: _type = _type()

    def connect(self, func) -> None:
        if not callable(func):
            raise TypeError("Function must be callable...")
        self.signal.connect(func)

    def setValue(self, v: Any) -> None:
        if not isinstance(v, self.___type):
            raise TypeError("Type mismatch occurred...")
        self.___value = v
        self.signal.emit(str(v))

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
    DOCTYPE: Variable = Variable(int)                       # ON DOCTYPE CHANGE

    # Services
    FONT: Variable = Variable(str)                          # ON FONT CHANGE
    ON_MAIN_WINDOW_LOAD: Variable = Variable(bool)          # ON MAIN WINDOW LOAD
    FOLDER: Variable = Variable(str)                        # ON MAIN FOLDER CHANGE
    OPEN_FILE: Variable = Variable(str)                     # ON FILE OPENING
    TOOL_WINDOW_CLOSED: Variable = Variable(bool)           # ON TOOL PRESENCE LOCK ELSE MAKE AVAILABLE CREATING ONE
    CLOSING_MAIN_WINDOW: Variable = Variable(bool)          # ON WINDOW CLOSE STOP EVERY SEPARATED THREAD

