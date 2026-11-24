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
from source.interface.shared import handleZoomEvent


class EditorGraphics(QsciScintilla):
    """Appearance of the code editor: colors, line number margin and style sheet"""

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
        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.verticalScrollBar().setObjectName("VScrollCode")
        self.setCaretLineVisible(True)
        self.setCaretLineBackgroundColor(QColor("#252526"))
        self.setCaretForegroundColor(QColor("#569CD6"))
        self.setPaper(QColor("#292727"))

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

    def loadStyles(self):
        """Load and apply CSS styles"""
        try:
            with open(find_path("editor.qss"), "r") as f:
                style = translateQSS(f.read())
                self.setStyleSheet(style)
        except FileNotFoundError:
            pass


class EditorLogic(EditorGraphics):
    """Behavior of the code editor: lexer, text features, shortcuts and search highlighting"""

    SEARCH_INDICATOR = 10
    CURRENT_MATCH_INDICATOR = 11
    EXECUTION_MARKER = 20
    EXECUTION_ARROW_MARKER = 21

    def __init__(self, mwt: QWidget, ext: str):
        super().__init__(mwt, ext)
        self.setupLexer(ext)
        self.configureTextFeatures()
        self.configureCommands()
        self.installEventFilter(self)
        self.SCN_ZOOM.connect(self._updateZoomMargin)

        self._setupSearchIndicator()
        self._setupExecutionMarker()
        self._search_matches = []
        self._current_match_index = -1

    def _updateZoomMargin(self):
        """Keep the line numbers visible at every zoom level"""
        self.setMarginWidth(0, "00000")

    def _resetZoom(self):
        self.zoomTo(0)

    def setupLexer(self, ext: str):
        """Setup the lexer matching the file extension"""
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

    def updateLexer(self, ext: str = None):
        """Replace the lexer with the one that matches the file extension"""
        if ext:
            self.ext = ext
        self.setupLexer(self.ext)

    def set_font(self):
        """Set editor font from database"""
        self.setFont(QFont(Database.FONT.getValue()))
    
    def _setupExecutionMarker(self):
        """Configure the markers of the line that the debugger runs next"""
        self.markerDefine(QsciScintilla.Background, self.EXECUTION_MARKER)
        self.setMarkerBackgroundColor(QColor("#1D4F3F"), self.EXECUTION_MARKER)
        self.markerDefine(QsciScintilla.RightArrow, self.EXECUTION_ARROW_MARKER)
        self.setMarkerBackgroundColor(QColor("#3FB950"), self.EXECUTION_ARROW_MARKER)
        self.setMarkerForegroundColor(QColor("#3FB950"), self.EXECUTION_ARROW_MARKER)
        self.setMarginType(1, QsciScintilla.SymbolMargin)
        self.setMarginWidth(1, 12)
        self.setMarginBackgroundColor(1, QColor("#2D2D30"))
        self.setMarginMarkerMask(1, 1 << self.EXECUTION_ARROW_MARKER)

    def setExecutionLine(self, line: int, follow: bool = False):
        """Highlight a line from 1 as the next one to run, or clear the highlight with -1"""
        self.markerDeleteAll(self.EXECUTION_MARKER)
        self.markerDeleteAll(self.EXECUTION_ARROW_MARKER)
        if line <= 0 or line > self.lines():
            return
        self.markerAdd(line - 1, self.EXECUTION_MARKER)
        self.markerAdd(line - 1, self.EXECUTION_ARROW_MARKER)
        if follow:
            self.ensureLineVisible(line - 1)

    def _setupSearchIndicator(self):
        """Configure the indicators used for search highlights"""
        # General matches: outlined box
        self.indicatorDefine(QsciScintilla.StraightBoxIndicator, self.SEARCH_INDICATOR)
        self.setIndicatorForegroundColor(QColor("#FF8C00"), self.SEARCH_INDICATOR) # Orange
        self.setIndicatorDrawUnder(True, self.SEARCH_INDICATOR)
        
        # Current match: same box style in another color
        self.indicatorDefine(QsciScintilla.StraightBoxIndicator, self.CURRENT_MATCH_INDICATOR)
        self.setIndicatorForegroundColor(QColor("#FF0000"), self.CURRENT_MATCH_INDICATOR) # Red for current
        self.setIndicatorDrawUnder(True, self.CURRENT_MATCH_INDICATOR)


    def _clearSearch(self):
        """Clear all search indicators and reset state"""
        self.clearIndicatorRange(0, 0, self.lines(), self.lineLength(self.lines()-1), self.SEARCH_INDICATOR)
        self.clearIndicatorRange(0, 0, self.lines(), self.lineLength(self.lines()-1), self.CURRENT_MATCH_INDICATOR)
        self._search_matches = []
        self._current_match_index = -1

    def _performSearch(self, prompt: str, use_regex: bool):
        """Find matches and highlight them"""
        self._clearSearch()
        if not prompt: return

        re = use_regex
        cs = False
        wo = False
        wrap = True
        forward = True
        
        cur_line, cur_index = self.getCursorPosition()

        found = self.findFirst(prompt, re, cs, wo, wrap, forward, 0, 0)
        while found:
            m_line, m_index, _, m_end = self.getSelection()
            
            if self._search_matches and (m_line, m_index) == self._search_matches[0][0:2]:
                break
                
            # Store (line, start, end) so we can redraw specific ranges
            self.fillIndicatorRange(m_line, m_index, m_line, m_end, self.SEARCH_INDICATOR)
            self._search_matches.append((m_line, m_index, m_end))
            
            found = self.findNext()
            if len(self._search_matches) > 5000: break

        self.setCursorPosition(cur_line, cur_index)
        if self._search_matches:
            self._jumpToNextMatch(cur_line, cur_index)

    def _jumpToNextMatch(self, cur_line, cur_index):
        """Select the first match at or after the cursor, wrapping to the first one"""
        for i, (line, index, end) in enumerate(self._search_matches):
            if line > cur_line or (line == cur_line and index >= cur_index):
                self._current_match_index = i
                self._updateCurrentMatchHighlight()
                self._scrollToMatch(i)
                return
        # Wrap around
        if self._search_matches:
            self._current_match_index = 0
            self._updateCurrentMatchHighlight()
            self._scrollToMatch(0)

    def _updateCurrentMatchHighlight(self):
        """Updates the indicators to highlight the current match distinctively"""
        self.clearIndicatorRange(0, 0, self.lines(), self.lineLength(self.lines()-1), self.CURRENT_MATCH_INDICATOR)
        
        if 0 <= self._current_match_index < len(self._search_matches):
            line, start, end = self._search_matches[self._current_match_index]
            
            self.clearIndicatorRange(line, start, line, end, self.SEARCH_INDICATOR)
            
            self.fillIndicatorRange(line, start, line, end, self.CURRENT_MATCH_INDICATOR)

    def _navigate(self, direction):
        """Move to the next or previous match, wrapping around"""
        if not self._search_matches: return
        
        if 0 <= self._current_match_index < len(self._search_matches):
            line, start, end = self._search_matches[self._current_match_index]
            self.clearIndicatorRange(line, start, line, end, self.CURRENT_MATCH_INDICATOR)
            self.fillIndicatorRange(line, start, line, end, self.SEARCH_INDICATOR)

        if direction == "next":
            self._current_match_index = (self._current_match_index + 1) % len(self._search_matches)
        elif direction == "prev":
            self._current_match_index = (self._current_match_index - 1) % len(self._search_matches)
        
        self._updateCurrentMatchHighlight()
        self._scrollToMatch(self._current_match_index)

    def _scrollToMatch(self, index):
        if 0 <= index < len(self._search_matches):
            line, col, _ = self._search_matches[index]
            self.setCursorPosition(line, col)
            self.ensureLineVisible(line)

    def getOccurrenceInfo(self):
        """Return (current match number, total matches) for the find counter"""
        if not self._search_matches: return (0, 0)
        return (self._current_match_index + 1, len(self._search_matches))


@EventRegister.register(FindShortcutEvent, "editor")
class Editor(EditorLogic):
    """Code editor of a single tab, driven by the find widget and zoom shortcuts"""

    def __init__(self, mwt: QWidget, ext: str, _id: int):
        super().__init__(mwt, ext)
        self._id = _id
        Database.ON_TAB_SELECTED.connect(self.onTabSelected)

    def onTabSelected(self):
        """Reset search when switching tabs"""
        self._clearSearch()

    def keyPressEvent(self, event):
        """Handle the zoom keys and the Find shortcut"""
        if handleZoomEvent(self, event, self.zoomIn, self._resetZoom):
            return
        if event.matches(QKeySequence.Find) or (
                event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_F):
            EventRegister.send(FindShortcutEvent(False), "editor/find")
            event.ignore()
            return
        super().keyPressEvent(event)

    def viewportEvent(self, event):
        if handleZoomEvent(self, event, self.zoomIn, self._resetZoom):
            return True
        return super().viewportEvent(event)

    def onFindShortcutEvent(self, event: FindShortcutEvent):
        """Run the search, navigation or close request of the find widget"""
        # Only process if this editor is the active one
        if Database.ON_TAB_SELECTED.getValue() != self._id:
            return

        if event.mustClose():
            self._clearSearch()
            return

        prompt = event.getPrompt()
        movement = event.getMovement()

        if movement != "none":
            self._navigate(movement)
        elif prompt is not None:
            self._performSearch(prompt, event.isRegex())
            
        # Send back info to update the widget counter
        EventRegister.send(
            FindShortcutEvent(False, occurrencies=self.getOccurrenceInfo()),
            "editor/find"
        )
