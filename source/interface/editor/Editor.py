from PyQt5.Qsci import QsciScintilla, QsciCommandSet, QsciCommand
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QKeySequence
from PyQt5.QtWidgets import QWidget, QSizePolicy

from source.comms import Database
from source.comms.events.FindShortcut import FindShortcutEvent
from source.comms.handlers import EventRegister
from source.filesystem import find_path
from source.interface.assets import translateQSS
from source.interface.editor.lexers import LexerFactory


class EditorGraphics(QsciScintilla):
    def __init__(self, mwt: QWidget, ext: str):
        super(QsciScintilla, self).__init__(mwt)
        self.ext = ext
        self.setObjectName("Editor")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setupUI()
        self.loadStyles()

    def setupUI(self):
        """Setup basic UI configurations"""
        # Widget
        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.verticalScrollBar().setObjectName("VScrollCode")
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#252526"))
        self.setCaretForegroundColor(QColor("#569CD6"))
        self.setPaper(QColor("#292727"))

        # Margin
        self.configureMargin()

    def configureMargin(self):
        """Configure line number margin"""
        self.setMarginType(0, QsciScintilla.NumberMargin)
        self.setMarginWidth(0, self.fontMetrics().width('00000'))
        self.setMarginOptions(QsciScintilla.TextMarginRightJustified)
        self.setMarginSensitivity(0, True)
        self.setMarginsFont(QFont("Monospace", 8))
        self.setMarginsBackgroundColor(QColor("#2D2D30"))
        self.setMarginsForegroundColor(QColor("#569CD6"))
        self.setMarginBackgroundColor(1, Qt.red)

    def loadStyles(self):
        """Load and apply CSS styles"""
        try:
            with open(find_path("editor.qss"), "r") as f:
                style = translateQSS(f.read())
                self.setStyleSheet(style)
        except FileNotFoundError:
            pass


class EditorLogic(EditorGraphics):
    def __init__(self, mwt: QWidget, ext: str):
        super().__init__(mwt, ext)
        self.content = None
        self.setupLexer(ext)
        self.configureTextFeatures()
        self.configureCommands()
        self.installEventFilter(self)

    def setupLexer(self, ext: str):
        """Setup the appropriate lexer based on current file and content"""
        lexer = LexerFactory.createLexer(self, ext)
        self.setLexer(lexer)

    def configureTextFeatures(self):
        """Configure text editing features like autocompletion and indentation"""
        self.setAutoCompletionShowSingle(True)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusExplicit)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(False)
        self.setAutoCompletionThreshold(1)

        self.setAutoCompletionFillups(" ")
        self.setAutoCompletionFillupsEnabled(True)
        self.setAutoCompletionSource(QsciScintilla.AcsAll)

        self.setAutoIndent(True)
        self.setTabIndents(True)
        self.setTabWidth(8)
        self.setIndentationWidth(8)
        self.setIndentationsUseTabs(True)

    def configureCommands(self):
        """Configure keyboard shortcuts and commands"""
        commands: QsciCommandSet = self.standardCommands()

        def add_command(cmd, seq):
            nonlocal commands
            if command := commands.find(cmd):
                command.setKey(seq)

        add_command(QsciCommand.LineCut, Qt.CTRL + Qt.Key_X)
        add_command(QsciCommand.LineCopy, Qt.CTRL + Qt.Key_C)
        add_command(QsciCommand.MoveSelectedLinesUp, Qt.SHIFT + Qt.CTRL + Qt.Key_Up)
        add_command(QsciCommand.MoveSelectedLinesDown, Qt.SHIFT + Qt.CTRL + Qt.Key_Down)

    def updateLexer(self, content: str = None):
        """Update lexer when content changes significantly"""
        if content:
            self.content = content
        lexer = LexerFactory.createLexer(self, self.content)
        self.setLexer(lexer)

    def set_font(self):
        """Set editor font from database"""
        self.setFont(QFont(Database.FONT.getValue()))

    def find_all_occurrences(self, pattern: str, use_regex: bool = False):
        occurrences = []

        # Start from the beginning
        line, index = 0, 0

        # Configure search flags
        re = use_regex  # Enable regex
        cs = True  # Case sensitive (set to False if needed)
        wo = False  # Whole word only
        wrap = False  # Don't wrap around
        forward = True  # Search forward

        # Find first occurrence
        found = self.findFirst(pattern, re, cs, wo, wrap, forward, line, index)

        while found:
            # Get current position
            line, index_start, _, index_end = self.getSelection()
            occurrences.append({
                'line': line,
                'start': index_start,
                'end': index_end,
                'text': self.selectedText()
            })

            # Find next occurrence
            found = self.findNext()

        return occurrences


class Editor(EditorLogic):
    def __init__(self, mwt: QWidget, ext: str):
        super().__init__(mwt, ext)
        # Connect font changes if needed
        # Database.FONT.connect(self.set_font)

    def keyPressEvent(self, event):
        """Handle key press events, particularly Find shortcut"""
        if event.matches(QKeySequence.Find) or (
                event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_F):
            EventRegister.send(FindShortcutEvent(), "editor")
            print(self.find_all_occurrences("MOVB", False)) # FUNZIONA
            event.ignore()
            return
        super().keyPressEvent(event)



# from PyQt5.Qsci import QsciScintilla, QsciCommandSet, QsciCommand, QsciDocument
# from PyQt5.QtCore import Qt
# from PyQt5.QtGui import QColor, QFont, QKeySequence
# from PyQt5.QtWidgets import QWidget, QSizePolicy
#
# from source.comms import Database
# from source.comms.events.FindShortcut import FindShortcutEvent
# from source.comms.handlers import EventRegister
# from source.filesystem import find_path
# from source.interface.assets import translateQSS
# from source.interface.editor.lexers import LexerFactory
#
#
# class Editor(QsciScintilla):
#     def __init__(self, mwt: QWidget, ext: str):
#         super(QsciScintilla, self).__init__(mwt)
#         self.setConfigurations()
#         self.setObjectName("Editor")
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
#         #Database.FONT.connect(self.set_font)
#         self.loadStyles()
#         self.setupLexer(ext)
#
#     def setupLexer(self, ext: str):
#         """Setup the appropriate lexer based on current file and content"""
#         lexer = LexerFactory.createLexer(self, ext)
#         self.setLexer(lexer)
#
#     def loadStyles(self):
#         try:
#             with open(find_path("editor.qss"), "r") as f:
#                 style = translateQSS(f.read())
#                 self.setStyleSheet(style)
#         except FileNotFoundError:
#             pass
#
#     def setConfigurations(self):
#         # Widget
#         self.setContentsMargins(0, 0, 0, 0)
#         self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
#         self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
#         self.verticalScrollBar().setObjectName("VScrollCode")
#         self.setCaretLineVisible(True)
#         self.setCaretLineBackgroundColor(QColor("#252526"))
#         self.setCaretForegroundColor(QColor("#569CD6"))
#         self.setPaper(QColor("#292727"))
#
#         # Margin
#         self.configureMargin()
#
#         self.configureTextFeatures()
#         self.installEventFilter(self)
#
#     def configureTextFeatures(self):
#         self.setAutoCompletionShowSingle(True)
#         self.setAutoCompletionUseSingle(QsciScintilla.AcusExplicit)
#         self.setAutoCompletionCaseSensitivity(False)
#         self.setAutoCompletionReplaceWord(False)
#         self.setAutoCompletionThreshold(1)
#
#         self.setAutoCompletionFillups(" ")
#         self.setAutoCompletionFillupsEnabled(True)
#         self.setAutoCompletionSource(QsciScintilla.AcsAll)
#
#         self.setAutoIndent(True)
#         self.setTabIndents(True)
#         self.setTabWidth(8)
#         self.setIndentationWidth(8)
#         self.setIndentationsUseTabs(True)
#         self.configureCommands()
#
#     def configureCommands(self):
#         commands: QsciCommandSet = self.standardCommands()
#
#         def add_command(cmd, seq):
#             nonlocal commands
#             if command := commands.find(cmd):
#                 command.setKey(seq)
#
#         add_command(QsciCommand.LineCut, Qt.CTRL + Qt.Key_X)
#         add_command(QsciCommand.LineCopy, Qt.CTRL + Qt.Key_C)
#         add_command(QsciCommand.MoveSelectedLinesUp, Qt.SHIFT + Qt.CTRL + Qt.Key_Up)
#         add_command(QsciCommand.MoveSelectedLinesDown, Qt.SHIFT + Qt.CTRL + Qt.Key_Down)
#
#     def keyPressEvent(self, event):
#         if event.matches(QKeySequence.Find) or (
#                 event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_F):
#             EventRegister.send(FindShortcutEvent(), "editor")
#             event.ignore()
#             return
#         super().keyPressEvent(event)
#
#     def configureMargin(self):
#         self.setMarginType(0, QsciScintilla.NumberMargin)
#         self.setMarginWidth(0, self.fontMetrics().width('00000'))
#         self.setMarginOptions(QsciScintilla.TextMarginRightJustified)
#         self.setMarginSensitivity(0, True)
#         self.setMarginsFont(QFont("Monospace", 8))
#         self.setMarginsBackgroundColor(QColor("#2D2D30"))
#         self.setMarginsForegroundColor(QColor("#569CD6"))
#         self.setMarginBackgroundColor(1, Qt.red)
#
#     def set_font(self):
#         self.setFont(QFont(Database.FONT.getValue()))
#
#     def updateLexer(self, content: str = None):
#         """Update lexer when content changes significantly"""
#         if content:
#             self.content = content
#         lexer = LexerFactory.createLexer(self, self.content)
#         self.setLexer(lexer)
