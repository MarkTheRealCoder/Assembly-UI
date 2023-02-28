from json import loads as getJSON

from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor

from Tools.Tools import find_path

"""
Questa classe ha il compito di:
Salvare tutti i token del file utilizzato
"""

class Lexer:

    colors = {
        "u": 0,
        "i": 1,
        "n": 2,
        "s": 3,
        "v": 4,
        "c": 5,
        "l": 6
    }

    def __init__(self, langFile: str):
        self.text: str = ""
        self.keywords: dict[str:dict[str, str]] = {}
        with open(find_path(langFile), "r").read() as decoding:
            decoding = getJSON(decoding)
            if decoding is not None:
                self.keywords["i"] = decoding

    def setColors(self, lex: QsciLexerCustom):
        lex.setColor(QColor("#E48300"), 1)
        lex.setColor(QColor("#0EA0A9"), 2)
        lex.setColor(QColor("#C1A402"), 3)
        lex.setColor(QColor("#0EA97C"), 4)
        lex.setColor(QColor("#A94B0E"), 5)
        lex.setColor(QColor("#06AC17"), 6)

    def setText(self, text: str):
        self.text = text

    def lookFor(self, _type: str, text: str):
        pass

    def getInfo(self):
        """
        Ciao
        01234
        Raul
        6789
        """

        """start = cursorPos[0] * 2
        for i in range(cursorPos[0]):
            start += len(textList[i])"""



