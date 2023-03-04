from PyQt5.Qsci import QsciScintilla, QsciLexerCustom
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QTextEdit, QLabel

from main.tools.languages.Languages import Lexer
from main.tools.Tools import SCALE, SCALEH


class Editor(QsciScintilla):
    def __init__(self, mwt: QWidget):
        super(QsciScintilla, self).__init__(mwt)
        self.setParent(mwt)
        self.setConfigurations()
        self.setObjectName("Editor")

    def setConfigurations(self):
        # Widget

        self.setFixedHeight(SCALEH(410, self.parent().height()))
        self.setFixedWidth(SCALE(670, self.parent().width()))
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
        self.setFixedHeight(SCALEH(210, self.parent().height()))
        self.setFixedWidth(SCALE(335, self.parent().width()))
        self.setContentsMargins(0, 0, 0, 0)


class Output(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__()
        self.setParent(mwt)
        self.setConfigurations()
        self.setObjectName("Output")

    def setConfigurations(self):
        self.setFixedHeight(SCALEH(210, self.parent().height()))
        self.setFixedWidth(SCALE(335, self.parent().width()))
        self.setContentsMargins(0, 0, 0, 0)


class IJVMLexer(QsciLexerCustom):
    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        # noinspection PyTypeChecker
        self._parent: QsciScintilla = self.parent()
        self.setDefaultPaper(QColor("#2F2C2C"))
        self.setDefaultColor(QColor("#979494"))
        self.lang = Lexer("languageIJVM.json")
        self.lang.setColors(self)

    def styleText(self, start, end):
        self.lang.setText(self._parent.text())
        info: list[tuple[int, int, int]] = self.lang.getInfo()
        if info:
            for i in info:
                self.defineStylingPosition(i[0], i[1], i[2])

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
