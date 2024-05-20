from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QSizePolicy, QApplication

from src.interface.components.codespace.Lexer import Lexer
from src.signals.Variables import DataBase


class Editor(QsciScintilla):
    def __init__(self, mwt: QWidget):
        super(QsciScintilla, self).__init__(mwt)
        self.setConfigurations()
        self.setObjectName("Editor")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
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
        self.installEventFilter(self)

    def configureTextFeatures(self):
        self.setAutoIndent(True)
        self.setIndentationWidth(2)
        self.setAutoCompletionReplaceWord(False)
        self.setAutoCompletionFillups(" ")
        self.setAutoCompletionFillupsEnabled(True)
        self.setAutoCompletionShowSingle(False)
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

    def configureMargin(self):
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, self.fontMetrics().width('00000'))
        self.setMarginOptions(QsciScintilla.TextMarginRightJustified)
        self.setMarginSensitivity(0, True)
        self.setMarginsFont(QFont("Monospace", 8))
        self.setMarginsBackgroundColor(QColor("#0B0C10"))
        self.setMarginsForegroundColor(QColor("#00AAFF"))
        self.setMarginBackgroundColor(1, Qt.red)

    def set_font(self):
        self.setFont(QFont(DataBase.FONT.getValue()))

    def eventFilter(self, obj, event):
        if event.type() == event.KeyPress:
            if event.key() == Qt.Key_X and event.modifiers() == Qt.ControlModifier:
                text = ""
                if not self.hasSelectedText():
                    line = self.getCursorPosition()[0]
                    text = self.text(line)
                    self.setSelection(line, 0, line+1, 0)
                else:
                    text = self.selectedText()
                self.removeSelectedText()
                clipboard = QApplication.clipboard()
                if text != "":
                    clipboard.setText(text)
                return True
        return super().eventFilter(obj, event)


