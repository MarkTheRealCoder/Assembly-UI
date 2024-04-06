from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import QColor, QFont


class Lexer(QsciLexerCustom):
    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        self._parent: QsciScintilla = self.parent()
        self.setDefaultPaper(QColor("#1F2833"))
        self.setDefaultColor(QColor("#258FF9"))
        self.setDefaultFont(QFont("Bahnschrift", 12))

    def styleText(self, start, end):
        pass

    def description(self, style):
        return "IJVM and 8088-assembly language lexer for Assembly-Stdio"

    def language(self):
        return "8088-assembly language lexer for Assembly-Stdio"
