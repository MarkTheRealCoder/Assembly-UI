from PyQt5.Qsci import QsciScintilla, QsciLexerCustom
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QWidget, QTextEdit, QLabel


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
        self.setPaper(QColor("#2F2C2C"))
        self.setColor(Qt.GlobalColor.white)
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


class Lexer(QsciLexerCustom):
    def __init__(self, parent=None):
        super(QsciLexerCustom, self).__init__(parent)
        self.setDefaultPaper(QColor("#2F2C2C"))

