from os import linesep

from PyQt5.Qsci import QsciScintilla, QsciLexerCustom
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QTextEdit, QLabel

from Tools.Languages.Languages import Lexer


class Editor(QsciScintilla):
    def __init__(self, mwt: QWidget):
        super(QsciScintilla, self).__init__(mwt)
        self.setParent(mwt)
        self.setConfigurations()
        self.setObjectName("Editor")

    def setConfigurations(self):
        # Widget
        self.setFixedHeight(410)
        self.setFixedWidth(670)
        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.verticalScrollBar().setObjectName("VScrollCode")
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#4F4B4B"))
        self.setCaretForegroundColor(QColor("#00AAFF"))
        self.setLexer(IJVMLexer(self))

        # Margin
        self.configureMargin()

        self.configureTextFeatures()

    def configureTextFeatures(self):
        self.setAutoIndent(True)
        self.setIndentationWidth(2)
        self.setAutoCompletionReplaceWord(True)
        self.setAutoCompletionFillups(" ")
        self.setAutoCompletionFillupsEnabled(True)
        self.setAutoCompletionShowSingle(True)

    def configureMargin(self):
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, self.fontMetrics().width('00000'))
        self.setMarginSensitivity(0, True)
        self.setMarginsBackgroundColor(QColor("#1E1E1E"))
        self.setMarginsForegroundColor(QColor("#00AAFF"))


class Input(QTextEdit):
    def __init__(self, mwt: QWidget):
        super(QTextEdit, self).__init__()
        self.setParent(mwt)
        self.setConfigurations()
        self.setObjectName("Input")

    def setConfigurations(self):
        self.setFixedHeight(210)
        self.setFixedWidth(335)
        self.setContentsMargins(0, 0, 0, 0)


class Output(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__()
        self.setParent(mwt)
        self.setConfigurations()
        self.setObjectName("Output")

    def setConfigurations(self):
        self.setFixedHeight(210)
        self.setFixedWidth(335)
        self.setContentsMargins(0, 0, 0, 0)


class IJVMLexer(QsciLexerCustom):
    _keywords = {}

    regexes = {
        "i": lambda i: r"(?<!\w)(?<=\s)*" + i + r"(?=\s|$)",
        "n": r"(0[Xx][0-9A-Fa-f]+|[0-9]+)(?=[\s,$\r]|$)",
        "s": r"(?<=^\.method )\b\w+\b(?=\s*\((?:\s*\w+|\w+\s*),\s*\w+\s*\))",
        "v": r"^(?<!\w)(?:\s*\w+)(?:^\s*|^$)",
        "c": r"\b(?>\w+)(?=\s*(?:0[Xx][0-9A-Fa-f]+|[0-9]+))",
        "l": r"(?:^|\s+)\w+:",
        "u": r"\b\w+\b"
    }

    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        # noinspection PyTypeChecker
        self._parent: QsciScintilla = self.parent()
        self.setDefaultPaper(QColor("#2F2C2C"))
        self.setDefaultColor(QColor("#979494"))
        self.lang = Lexer("languageIJVM.json")
        self.lang.setColors(self)

    def styleText(self, start, end):
        cursorPos = self._parent.getCursorPosition()
        text: str = self._parent.text()
        textList = text.split(linesep)
        print(text)
        self.lang.setText(text)
        #generator = self.lang.getInfo()
        #for i in next(generator):
        #    self.defineStylingPosition(i)

    def defineStylingPosition(self, start: int, style: int, length: int):
        self.startStyling(start)
        self.setStyling(length, style)

    def description(self, style):
        return "IJVM-assembly language lexer for Assembly-Stdio"

    def language(self):
        return "IJVM language"


class BOBBLexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super(QsciLexerCustom, self).__init__(parent)
        self.setDefaultPaper(QColor("#2F2C2C"))
        self.setDefaultColor(QColor("#979494"))

    def description(self, style):
        return "8088-assembly language lexer for Assembly-Stdio"

    def language(self):
        return "8088 language"
