from typing import Literal
from json import loads as getJSON
from os import linesep

import regex
from PyQt5.Qsci import QsciLexerCustom
from PyQt5.QtGui import QColor

from src.tools.Tools import find_path, isEmpty

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

    def __init__(self, lang_file: str):
        self.database = Data()
        self.regex = {}
        with open(find_path(lang_file), "r") as decoding:
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

    def getInfo(self, text: str) -> list[tuple[int, int, int]]:
        ts = text.split(linesep)
        self.indexing(ts)
        informations: list[tuple[int, int, int]] = []
        for lineNum, line in enumerate(ts):
            csp = calculate(lineNum, ts)
            informations += self.analyzeLine(line, csp)
        return informations

    def analyzeLine(self, txt: str, csp: int) -> list[tuple[int, int, int]]:
        result: list[tuple[int, int, int]] = []
        return result

    def indexing(self, ts: list[str]) -> dict[str: list[tuple[int, int, int, int] or tuple[int, int]]]:
        declarators: dict[str: list[tuple[int, int, int, int] or tuple[int, int]]] = {}
        for k in ["constants", "main", "variables", "methods", "comments", "labels"]:
            declarators.setdefault(k, [])
        for num, line in enumerate(ts):
            if isEmpty(line):
                continue
            line, comment = self.removeComment(line, num)
            ts[num - 1] = line
            if comment:
                declarators["comments"].append(comment)
            line, label = self.removeLabel(line, num)
            ts[num - 1] = line
            if label:
                declarators["labels"].append(label)
            type_, elem, crd = self.findDeclarator(line, num)
            new_dcl = self.update_temp_dcl(type_, elem, crd)

    @staticmethod
    def ___save_values(func):
        def wrapper(*args, **kwargs):
            pass
        return wrapper()

    @___save_values
    def update_temp_dcl(self,
                        type_: Literal["open", "close"],
                        elem: Literal["constants", "variables", "methods", "main"],
                        crd: int):
        pass


"""
.constant
    OBJREF 0x40
    endline 0x3b
.end-constant

.main
    .var
        a
        b
    .end-var

    LDC_W OBJREF
    INVOKEVIRTUAL input
    LDC_W OBJREF
    INVOKEVIRTUAL input
    istore b
    istore a

    halt
.end-main


.method mul(i, j)
    ILOAD j
    IFEQ zero
    IINC j  -1
    ILOAD i
    IFEQ zero
    LDC_W OBJREF
    ILOAD i
    ILOAD j
    INVOKEVIRTUAL mul
    ILOAD i
    IADD
    GOTO fine
zero:
    BIPUSH 0x0
fine:
    IRETURN
.end-method


.method mod (a, b)
    ILOAD a
    IFEQ stop
    ILOAD a
    ILOAD b
    ISUB
    IFLT stop
    LDC_W OBJREF
    ILOAD a
    ILOAD b
    ISUB
    ILOAD b
    INVOKEVIRTUAL mod
    GOTO fine
stop:
    ILOAD a
fine:
    IRETURN
.end-method

.method div (a, b)
    ILOAD a
    ILOAD b
    ISUB
    IFLT stop
    LDC_W OBJREF
    ILOAD a
    ILOAD b
    ISUB
    ILOAD b
    INVOKEVIRTUAL div
    BIPUSH 1
    IADD
    GOTO fine
stop:
    BIPUSH 0x0
fine:
    IRETURN
.end-method
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


def calculate(ln: int, tl: list[str]):
    pos: int = 0
    for i in range(ln):
        pos += len(tl[i])
    pos += ln * 2
    return pos
