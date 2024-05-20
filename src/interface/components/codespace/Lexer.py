from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import QColor, QFont
from regex import regex


class Lexer(QsciLexerCustom):
    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        self._parent: QsciScintilla = self.parent()
        self.setDefaultPaper(QColor("#1F2833"))
        self.setDefaultColor(QColor("#258FF9"))
        self.setDefaultFont(QFont("Bahnschrift", 12))

    def styleText(self, start, end):
        #print("Tokenized")
        prototype = regex.compile("\\.\\w+|\\W|\\w+|\\s")
        text = self._parent.text()[start:end]
        #print(prototype.findall(text))

    def description(self, style):
        return "IJVM and 8088-assembly language lexer for Assembly-Stdio"

    def language(self):
        return "a8088"
