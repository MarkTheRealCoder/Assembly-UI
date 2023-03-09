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
        "instructions": 1,
        "numbers": 2,
        "subroutines": 3,
        "variables": 4,
        "constants": 5,
        "labels": 6,
        "unidentified": 7,
        "comments": 8,
        "parameters": 4,
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
                _list = self.regex.get("instructions")
                self.regex["instructions"] = lambda i: _list[0] + regex.escape(i) + _list[1]

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
        self.indexing(ts)
        informations: list[tuple[int, int, int]] = []
        csp = 0
        for lineNum, line in enumerate(ts):
            csp = calculate(lineNum, ts)
            informations += self.analyzeLine(line, csp)
        return informations

    def analyzeLine(self, txt: str, csp: int) -> list[tuple[int, int, int]]:
        result: list[tuple[int, int, int]] = []
        return result

    def indexing(self, ts: list[str]):
        c = False
        m = False
        s = ""
        v = False
        for num, line in enumerate(ts):
            match = regex.search(self.regex.get("comments"), line)
            if match:
                line = line[0:match.start()]
            if line == "":
                continue
            uifd = regex.findall(self.regex.get("unidentified"), line)
            if c:
                self.findConstants(line, uifd)
            elif s != "":
                if v:
                    self.findVariables(line, uifd, s)
            c, m, v = self.findDeclarators(uifd, c, m, v)
            if m:
                s = self.findMethods(line, uifd)
            else:
                s = ""
            self.findLabels(line, uifd, num)

    def findConstants(self, txt: str, uifd: list[str]):
        match = regex.match(self.regex.get("constants"), txt)
        if match:
            constant = match.group(0)
            val = match.group(1)
            if val:
                uifd.remove(val)
                uifd.remove(constant)
            self.database.setConstants(constant)

    def findVariables(self, txt: str, uifd: list[str], scope: str):
        match = regex.match(self.regex.get("variables"), txt)
        if match:
            variable = match.group()
            self.database.setVariables(variable, scope)
            uifd.remove(variable)

    def findDeclarators(self, uifd: list[str], constant: bool, method: bool, variable: bool):
        words = uifd
        if words:
            constant = (words[0] == ".constant") if not constant else not words[0] == ".end-constant"
            method = (words[0] in [".method", ".main"]) if not constant else words[0] not in [".end-method", ".end-main"]
            variable = (words[0] == ".var") if not constant else not words[0] == ".end-var"
        if words[0] in [".constant", ".end-constant", ".end-method", ".end-main", ".method", ".main", ".var", ".end-var"]:
            uifd.remove(words[0])
        return constant, method, variable

    def findMethods(self, txt: str, uifd: list[str]):
        search = regex.search(self.regex.get("subroutines"), txt)
        method = search.group()
        uifd.remove(method)
        txt = txt[search.end():]
        params = regex.findall(self.regex.get("parameters"), txt)
        for i in params:
            uifd.remove(i)
            self.database.setVariables(i, method)
        self.database.setSubroutines(method)
        return method

    def findLabels(self, txt: str, uifd: list[str], line: int):
        search = regex.search(self.regex.get("labels"), txt)
        if search:
            label = search.group()
            uifd.remove(label)
            self.database.setLabels(label, line)


"""
C = TRUE IF W=s AND C=FALSE
C = FALSE IF W=s2 AND C=TRUE
"""


class Data:

    def __init__(self):
        # K: INSTRUCTION, V: DATA TYPE
        self.__keywords: dict[str:str] = {}
        # K: SCOPE, V: LIST OF VARIABLE's NAMES
        self.__variables: dict[str:list[str]]
        # K: None, V: LIST OF CONSTANT's NAMES
        self.__constants: list[str] = []
        # K: LABEL, V: LINE
        self.__labels: dict[str:int] = {}
        # K: SUBROUTINE, V: LIST OF PARAMETERS
        self.__subroutines: list[str] = []

    def setKeywords(self, keywords: dict[str:str]):
        self.__keywords = keywords

    def setSubroutines(self, val: str):
        if val in self.__subroutines:
            pass

    def setVariables(self, val: str, scope: str):
        pass

    def setConstants(self, val: str):
        pass

    def setLabels(self, val: str, ln: int):
        pass

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


