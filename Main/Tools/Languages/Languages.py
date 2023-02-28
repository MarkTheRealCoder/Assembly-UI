from json import loads as getJSON
from os import linesep
from typing import Any

import regex
from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor

from Tools.Tools import find_path

"""
Questa classe ha il compito di:
Salvare tutti i token del file utilizzato
"""


class Lexer:
    LAST = 0
    CURR = 1

    colors = {
        "u": 0,
        "i": 1,
        "n": 2,
        "s": 3,
        "v": 4,
        "c": 5,
        "l": 6
    }

    def __init__(self, langfile: str):
        self.text: str = ""
        self.keywords: dict[str:dict[str: Any]] = {}
        self.__listofkeys: list[str] = []
        with open(find_path(langfile), "r") as decoding:
            decoding = getJSON(decoding.read())
            if decoding is not None:
                self.keywords["i"] = decoding.get("i")
                self.regex = decoding.get("r")
                _list = self.regex.get("i")
                self.regex["i"] = lambda i: regex.compile(_list[0] + i + _list[1], regex.IGNORECASE)

    def setColors(self, lex: QsciLexerCustom):
        lex.setColor(QColor("#E48300"), 1)
        lex.setColor(QColor("#0EA0A9"), 2)
        lex.setColor(QColor("#C1A402"), 3)
        lex.setColor(QColor("#0EA97C"), 4)
        lex.setColor(QColor("#A94B0E"), 5)
        lex.setColor(QColor("#06AC17"), 6)

    def setText(self, text: str):
        self.text = text

    def lookFor(self):
        ts = self.text.split(linesep)

        for i in ts:
            _list = regex.findall(self.regex.get("u"), i)
            _tmp = {}
            for j in self.regex.keys():

                if j == "i":
                    for k in self.keywords.get("i").keys():
                        _tmp[j] = self.regex.get(j)(k).findall(i)

                elif j != "u":
                    _tmp[j] = regex.findall(self.regex.get(j), i)
            self.merge(_tmp)

    def merge(self, tmp: dict):
        pass

    def getInfo(self):
        pass

"""start = cursorPos[0] * 2
        for i in range(cursorPos[0]):
            start += len(textList[i])"""



