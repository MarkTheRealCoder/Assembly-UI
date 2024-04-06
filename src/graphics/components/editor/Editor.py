from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QSizePolicy

from src.graphics.components.editor.Lexer import Lexer
from src.tools.Variables import DataBase


class Editor(QsciScintilla):
    def __init__(self, mwt: QWidget):
        super(QsciScintilla, self).__init__(mwt)
        self.setConfigurations()
        self.setObjectName("Editor")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        DataBase.FONT.connect(self.set_font)

    def setConfigurations(self):
        # Widget
        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.verticalScrollBar().setObjectName("VScrollCode")
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#4F4B4B"))
        self.setCaretForegroundColor(QColor("#00AAFF"))
        self.setPaper(QColor("#1F2833"))
        self.setLexer(Lexer(self))

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
        self.setMarginsBackgroundColor(QColor("#0B0C10"))
        self.setMarginsForegroundColor(QColor("#00AAFF"))

    def set_font(self):
        self.setFont(QFont(DataBase.FONT.getValue()))


