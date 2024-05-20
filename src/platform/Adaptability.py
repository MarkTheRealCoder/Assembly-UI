import os

from PyQt5.QtCore import QSize
from regex import regex


def translateQSS(style: str):
    variables: dict[str: str] = {}
    index = style.find("variables")
    last_index = style.find("}", index)
    substring_variables = style[index:last_index]
    substring_variables = substring_variables.replace("variables", "").replace("{", "")
    raw = substring_variables.split(";")  # comments_free.split(";")
    for i in raw:
        try:
            k, v = i.split(":")
            variables[k.strip()] = v.strip()
        except Exception as e:
            del e
    style = style[last_index + 1:]
    matches: list[regex.Match] = regex.findall(r"(var\s*\((.*)\))", style)
    for s, r in matches:
        style = style.replace(s, variables.get(r))
    return style


def isWindows():
    return os.name == "nt"


class Desktop:
    DESKTOP_SIZE: QSize = None

    @staticmethod
    def sizeHint(wr: float, hr: float) -> QSize or None:
        if Desktop.DESKTOP_SIZE is not None:
            ds = Desktop.DESKTOP_SIZE
            return QSize(int(ds.width() * wr), int(ds.height() * hr))
        return None

    @staticmethod
    def getDesktopSize() -> QSize:
        return Desktop.DESKTOP_SIZE

    @staticmethod
    def setDesktopSize(size: QSize):
        if isinstance(size, QSize):
            Desktop.DESKTOP_SIZE = size
