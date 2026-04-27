from typing import Literal

from PyQt5.QtCore import QEvent

from source.comms.events import Event


class FindShortcutEvent(Event):

    Ready = QEvent.registerEventType()

    def __init__(self, close: bool, prompt: str = None, regex: bool = False, occurrencies: tuple[int, int] = None, movement: Literal["next", "prev", "none"] = "none"):
        super().__init__(FindShortcutEvent.Ready)
        self.___close = close
        self.___occurrencies = occurrencies if occurrencies is not None else (0, 0)
        self.___movement = movement
        self.___prompt = prompt
        self.___regex = regex

    def getOccurrencies(self) -> tuple[int, int]:
        """Returns a tuple with the current occurrence index and total occurrences."""
        return self.___occurrencies

    def mustClose(self) -> bool:
        return self.___close

    def getMovement(self) -> str:
        return self.___movement

    def getPrompt(self) -> str:
        return self.___prompt

    def isRegex(self) -> bool:
        return self.___regex

    @staticmethod
    def gtype():
        return FindShortcutEvent.Ready