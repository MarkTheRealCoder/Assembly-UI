from PyQt5.Qsci import QsciScintilla
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont
from PyQt5.QtWidgets import QWidget, QSizePolicy, QApplication

from source.comms import Database
from source.filesystem import find_path
from source.interface.assets.qstylesheets import translateQSS
from source.interface.editor.lexers.Lexer import LexerFactory


class Editor(QsciScintilla):
    def __init__(self, mwt: QWidget, content: str = None):
        super(QsciScintilla, self).__init__(mwt)
        self.content = content
        self.setConfigurations()
        self.setObjectName("Editor")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        Database.FONT.connect(self.set_font)
        Database.ON_TAB_SELECTED.connect(self.onTabChanged)
        self.loadStyles()
        self.setupLexer()

    def onTabChanged(self):
        """Called when tab selection changes to update lexer if needed"""
        self.setupLexer()

    def setupLexer(self):
        """Setup the appropriate lexer based on current file and content"""
        lexer = LexerFactory.createLexer(self, self.content)
        self.setLexer(lexer)

    def loadStyles(self):
        try:
            with open(find_path("editor.qss"), "r") as f:
                style = translateQSS(f.read())
                self.setStyleSheet(style)
        except FileNotFoundError:
            pass

    def setConfigurations(self):
        # Widget
        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.verticalScrollBar().setObjectName("VScrollCode")
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#252526"))
        self.setCaretForegroundColor(QColor("#569CD6"))
        self.setPaper(QColor("#1E1E1E"))

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
        self.setMarginsBackgroundColor(QColor("#2D2D30"))
        self.setMarginsForegroundColor(QColor("#569CD6"))
        self.setMarginBackgroundColor(1, Qt.red)

    def set_font(self):
        self.setFont(QFont(Database.FONT.getValue()))

    def updateLexer(self, content: str = None):
        """Update lexer when content changes significantly"""
        if content:
            self.content = content
        lexer = LexerFactory.createLexer(self, self.content)
        self.setLexer(lexer)

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


