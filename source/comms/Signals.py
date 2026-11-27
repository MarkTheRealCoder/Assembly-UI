from typing import Any

from PyQt5.QtCore import pyqtSignal, QObject


class Variable(QObject):
    signal = pyqtSignal(str)

    def __init__(self, _type: type):
        super(QObject, self).__init__()
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

    def getValue(self) -> Any:
        return self.___value


class DataBase:

    # Tabs
    ON_TAB_CLOSE: Variable = Variable(int)                  # ON TAB CLOSE
    ON_TAB_SELECTED: Variable = Variable(int)               # ON TAB SELECTED

    # Global events
    ON_FILE_REPLACED: Variable = Variable(str)              # ON FILE REPLACED FROM A FILE DIALOG
    ON_SPLITTER_DRAG: Variable = Variable(bool)             # TRUE WHILE THE USER DRAGS A SPLITTER HANDLE
    ON_EDITOR_ZOOM: Variable = Variable(int)                # ZOOM LEVEL SHARED BY ALL THE EDITORS

    # Execution
    ON_EXECUTION_LINE: Variable = Variable(tuple)           # (PATH, LINE) OF THE NEXT INSTRUCTION, LINE -1 TO CLEAR
    ON_DIAGNOSTICS: Variable = Variable(tuple)              # (PATH, [Diagnostic]) REPORTED BY THE LAST RUN, [] TO CLEAR

