from os import linesep
from typing import Literal


class AbstractType:

    def __init__(self, name: str, trace: str):
        self.type_name: str = name
        self.type_trace: str = trace

    def name(self):
        return self.type_name

    def trace(self):
        return self.type_trace


class Region:
    def __init__(self, pos: int, length: int, style: int):
        self.pos = pos
        self.len = length
        self.style = style
        a = Literal["A"]

    def extract(self, w: Literal["a", "p", "l", "s"]):
        if w == "a":
            return self.pos, self.len, self.style
        elif w == "p":
            return self.pos
        elif w == "l":
            return self.len
        elif w == "s":
            return self.style


class Lang:

    INSTRUCTION = "<instruction>"
    CONSTANT = "<constant>"
    VARIABLE = "<variable>"
    LABEL = "<label>"
    NONE = "<none>"
    VALUE = "<value>"

    def __init__(self):
        self.bindings: dict[str: list[str or AbstractType]] = {
            Lang.INSTRUCTION: [],
            Lang.VALUE: [],
            Lang.CONSTANT: [],
            Lang.VARIABLE: [],
            Lang.LABEL: [],
            Lang.NONE: []
        }
        self.calculator = lambda x: x

        self.text = ""

    def bind(self, _type: str, _element: str or AbstractType):
        self.bindings.get(_type).append(_element)

    def tokenize(self, txt: str) -> list[Region]:
        ts: list[str] = txt.split(linesep)
        regions: list[Region] = []
        for n, l in enumerate(ts):
            regions.append(Region(*self.__recognize__(n, l)))
        return regions

    def __recognize__(self, number: int, line: str) -> tuple[int, int, int]:
        tokens: list[str] = []
        for i in range(len(line)):

