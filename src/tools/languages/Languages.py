from json import loads as getJSON
from os import linesep

import regex
from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor

from src.tools.Tools import find_path

"""
Questa classe ha il compito di:
Salvare tutti i token del file utilizzato
"""


class Lexer:

    colors = {
        "i": 1,
        "n": 2,
        "s": 3,
        "v": 4,
        "c": 5,
        "l": 6,
        "u": 7
    }

    def __init__(self, langFile: str):
        self.text: str = ""
        self.database = Data()
        self.regex = {}
        with open(find_path(langFile), "r") as decoding:
            code = decoding.read()
            decoding.close()
            decoding = getJSON(code)
            if decoding is not None:
                self.database.setKeywords(decoding.get("i"))
                self.regex = decoding.get("r")
                _list = self.regex.get("i")
                self.regex["i"] = lambda i: _list[0] + regex.escape(i) + _list[1]

    def setColors(self, lex: QsciLexerCustom):
        lex.setColor(QColor("#E48300"), 1)
        lex.setColor(QColor("#0EA0A9"), 2)
        lex.setColor(QColor("#C1A402"), 3)
        lex.setColor(QColor("#0EA97C"), 4)
        lex.setColor(QColor("#A94B0E"), 5)
        lex.setColor(QColor("#06AC17"), 6)
        lex.setColor(QColor("#FE1717"), 7)

    def setText(self, text: str):
        self.text = text

    def getInfo(self) -> list[tuple[int, int, int]]:
        ts = self.text.split(linesep)
        self.findTokens(ts)
        informations: list[tuple[int, int, int]] = []
        csp = 0
        for lineNum, line in enumerate(ts):
            csp = calculate(lineNum, ts)
            informations += self.analyzeLine(line, csp)
        return informations

    def analyzeLine(self, txt: str, csp: int) -> list[tuple[int, int, int]]:
        uMatches = regex.finditer(self.regex.get("u"), txt, overlapped=False)
        unidentified: list[tuple[str, int]] = [(str(i.group(0)), i.start(0)) for i in uMatches]
        matches: dict[str:tuple[int, int]] = self.database.match(unidentified)
        result: list[tuple[int, int, int]] = []
        err = Lexer.colors.get("u")
        for match in matches.keys():
            tmp = matches.get(match)
            if tmp[1] == err and regex.match(self.regex.get("n"), match) is not None:
                tmp = (tmp[0], Lexer.colors.get("n"))
            result.append((csp + tmp[0], tmp[1], len(match)))
            print(f"RESULT: \n{result}")
        return result

    def findTokens(self, ts: list[str]):
        for lineNum, line in enumerate(ts):
            csp = calculate(lineNum, ts)
            matches = {}
            for i in self.regex.keys():
                if i not in ["i", "u", "n"]:
                    matches[i] = [(j.group(0), j.start(0)) for j in regex.finditer(self.regex.get(i), line)]
            for match in matches.keys():
                vals = matches.get(match)
                print(match, vals)
                if vals:
                    pass


class Data:

    def __init__(self):
        self.__keywords = {}
        self.__variables = {}
        self.__constants = {}
        self.__labels = {}
        self.__subroutines = {}

    def setKeywords(self, keywords: dict[str:str]):
        self.__keywords = keywords

    def setSubroutines(self, val: str, ln: int, params: str):
        if val not in self.__subroutines.keys():
            self.__subroutines[val] = [ln, params]
        else:
            _ln, _params = self.__subroutines.get(val)
            if _ln != ln or _params != params:
                self.__subroutines[val] = [ln, params]

    def setVariables(self, val: str, ln: int, scope: str):
        if val not in self.__variables.keys():
            self.__variables[val] = [ln, scope]
        else:
            _ln, _scope = self.__variables.get(val)
            if _ln != ln or _scope != scope:
                self.__variables[val] = [ln, scope]

    def setConstants(self, val: str, ln: int):
        if val not in self.__constants.keys():
            self.__constants[val] = ln
        else:
            _ln = self.__constants.get(val)
            if _ln != ln:
                self.__constants[val] = ln

    def setLabels(self, val: str, ln: int):
        if val not in self.__labels.keys():
            self.__labels[val] = ln
        else:
            _ln = self.__labels.get(val)
            if _ln != ln:
                self.__labels[val] = ln

    def match(self, tokens: list[tuple[str, int]]) -> dict[str:tuple[int, int]]:
        matches: dict[str: tuple[int, int]] = {}
        _tokens: dict = {
            "i": self.__keywords.keys(),
            "l": self.__labels.keys(),
            "s": self.__subroutines.keys(),
            "c": self.__constants.keys(),
            "v": self.__variables.keys()
        }
        for j in tokens:
            for i in _tokens.keys():
                if j[0] in _tokens.get(i):
                    matches[j[0]] = (j[1], Lexer.colors.get(i))
                    break
            else:
                matches[j[0]] = (j[1], Lexer.colors.get("u"))
        return matches


def calculate(ln: int, tl: list[str]):
    pos: int = 0
    for i in range(ln):
        pos += len(tl[i])
    pos += ln * 2
    return pos


