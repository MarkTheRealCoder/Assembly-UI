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
        self.regex = {}
        with open(find_path(lang_file), "r") as decoding:
            code = decoding.read()
            decoding.close()
            decoding = getJSON(code)

    def setColors(self, lex: QsciLexerCustom):
        lex.setColor(QColor("#E48300"), 1)
        lex.setColor(QColor("#0EA0A9"), 2)
        lex.setColor(QColor("#C1A402"), 3)
        lex.setColor(QColor("#0EA97C"), 4)
        lex.setColor(QColor("#A94B0E"), 5)
        lex.setColor(QColor("#06AC17"), 6)
        lex.setColor(QColor("#FE1717"), 7)

    def getInfo(self, text: str):
        ts = text.split(linesep)



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


class Tokens:

    def __init__(self):
        self.___map: dict[
            str:                        # token name
            dict[
                str:                    # data's category
                list[int]
                or str
                or int
            ]
        ]


"""
Informazioni che ho:
- Quali sono le parole chiave
- Cosa richiedono come parametri
- Dove esse possono essere utilizzate

Informazioni che non ho:
- Qual'è la posizione dei token nel testo
- Quali parametri verranno dati 
- Dove verranno utilizzate
"""

