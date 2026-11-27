from PyQt5.Qsci import QsciScintilla, QsciCommandSet, QsciCommand
import re

from PyQt5.QtCore import Qt, QPoint, QTimer
from PyQt5.QtGui import QColor, QKeySequence
from PyQt5.QtWidgets import QWidget, QSizePolicy, QToolTip

from source.comms import Database
from source.comms.events import FindShortcutEvent
from source.comms.handlers import EventRegister
from source.filesystem import find_path
from source.interface import handleZoomEvent
from source.interface.assets import translateQSS, editorFont
from source.interface.editor.lexers import LexerFactory
from source.interpreter import Diagnostic


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
        self.setMarginsFont(editorFont(9))
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
    ERROR_INDICATOR = 12
    WARNING_INDICATOR = 13
    EXECUTION_MARKER = 20
    EXECUTION_ARROW_MARKER = 21
    ERROR_MARKER = 22
    WARNING_MARKER = 23
    ERROR_LINE_MARKER = 24

    ___DWELL_MS = 400
    ___COMPLETION_DELAY_MS = 400
    ___WORD = re.compile(r"[A-Za-z0-9_.\-]+")

    def __init__(self, mwt: QWidget, ext: str):
        super().__init__(mwt, ext)
        self.setupLexer(ext)
        self.configureTextFeatures()
        self.configureCommands()
        self.installEventFilter(self)
        self.SCN_ZOOM.connect(self._updateZoomMargin)

        self._setupSearchIndicator()
        self._setupExecutionMarker()
        self._setupDiagnostics()
        self._setupCompletion()
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
        if hasattr(self, "_completion_timer"):
            self._refreshCompletions()

    def configureTextFeatures(self):
        """Configure text editing features like autocompletion and indentation"""
        self.setAutoCompletionShowSingle(True)
        self.setAutoCompletionUseSingle(QsciScintilla.AcusExplicit)
        self.setAutoCompletionCaseSensitivity(False)
        self.setAutoCompletionReplaceWord(False)
        self.setAutoCompletionThreshold(1)

        self.setAutoCompletionFillups(" ")
        self.setAutoCompletionFillupsEnabled(True)
        # Only the keywords and the symbols that the lexer finds outside comments, never every word of the file.
        self.setAutoCompletionSource(QsciScintilla.AcsAPIs)

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

        # keyPressEvent cuts or copies the line when nothing is selected, so the line commands need no keys.
        add_command(QsciCommand.LineCut, 0)
        add_command(QsciCommand.LineCopy, 0)
        add_command(QsciCommand.SelectionCut, Qt.CTRL + Qt.Key_X)
        add_command(QsciCommand.SelectionCopy, Qt.CTRL + Qt.Key_C)
        add_command(QsciCommand.MoveSelectedLinesUp, Qt.SHIFT + Qt.CTRL + Qt.Key_Up)
        add_command(QsciCommand.MoveSelectedLinesDown, Qt.SHIFT + Qt.CTRL + Qt.Key_Down)
    
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
        self.setMarginMarkerMask(
            1, (1 << self.EXECUTION_ARROW_MARKER) | (1 << self.ERROR_MARKER) | (1 << self.WARNING_MARKER)
        )

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

    def _setupDiagnostics(self):
        """Configure the squiggles, margin markers and tooltips of the errors reported by the interpreter"""
        self._diagnostics: list[tuple[int, Diagnostic]] = []

        self.indicatorDefine(QsciScintilla.SquiggleIndicator, self.ERROR_INDICATOR)
        self.setIndicatorForegroundColor(QColor("#F14C4C"), self.ERROR_INDICATOR)
        self.indicatorDefine(QsciScintilla.SquiggleIndicator, self.WARNING_INDICATOR)
        self.setIndicatorForegroundColor(QColor("#CCA700"), self.WARNING_INDICATOR)

        self.markerDefine(QsciScintilla.Circle, self.ERROR_MARKER)
        self.setMarkerBackgroundColor(QColor("#F14C4C"), self.ERROR_MARKER)
        self.setMarkerForegroundColor(QColor("#F14C4C"), self.ERROR_MARKER)
        self.markerDefine(QsciScintilla.Circle, self.WARNING_MARKER)
        self.setMarkerBackgroundColor(QColor("#CCA700"), self.WARNING_MARKER)
        self.setMarkerForegroundColor(QColor("#CCA700"), self.WARNING_MARKER)
        self.markerDefine(QsciScintilla.Background, self.ERROR_LINE_MARKER)
        self.setMarkerBackgroundColor(QColor("#3C1F1F"), self.ERROR_LINE_MARKER)

        self.SendScintilla(QsciScintilla.SCI_SETMOUSEDWELLTIME, self.___DWELL_MS)
        self.SCN_DWELLSTART.connect(self._showDiagnosticTooltip)
        self.SCN_DWELLEND.connect(lambda *_: QToolTip.hideText())
        self.textChanged.connect(self._dropEditedDiagnostics)

    def _diagnosticRange(self, diagnostic: Diagnostic) -> tuple[int, int]:
        """Return the columns (start, end) to underline on the line of the diagnostic"""
        text = self.text(diagnostic.line - 1).rstrip("\r\n")
        if diagnostic.column < 0:
            start = len(text) - len(text.lstrip())
            return start, len(text.rstrip())
        column = min(diagnostic.column, len(text))
        token = diagnostic.token
        if token and token.strip() and text[column:column + len(token)] == token:
            return column, column + len(token)
        if column < len(text) and not text[column].isspace():
            match = self.___WORD.match(text, column)
            return column, match.end() if match else column + 1
        # The error is at the end of the line or on blanks, as for a missing operand: underline the text before it.
        end = len(text[:column].rstrip())
        start = end
        while start > 0 and not text[start - 1].isspace():
            start -= 1
        return start, end

    def setDiagnostics(self, diagnostics: list[Diagnostic], follow: bool = False):
        """Underline the errors and warnings of the last run and mark their lines, replacing the previous ones"""
        self.clearDiagnostics()
        for diagnostic in diagnostics:
            if diagnostic.line <= 0 or diagnostic.line > self.lines():
                continue
            line = diagnostic.line - 1
            error = diagnostic.severity == "error"
            start, end = self._diagnosticRange(diagnostic)
            if end > start:
                self.fillIndicatorRange(line, start, line, end,
                                        self.ERROR_INDICATOR if error else self.WARNING_INDICATOR)
            handle = self.markerAdd(line, self.ERROR_MARKER if error else self.WARNING_MARKER)
            if error:
                self.markerAdd(line, self.ERROR_LINE_MARKER)
            self._diagnostics.append((handle, diagnostic))
        if follow and self._diagnostics:
            self.ensureLineVisible(self._diagnostics[0][1].line - 1)

    def clearDiagnostics(self):
        """Remove every error and warning shown in the editor"""
        self._diagnostics = []
        last = max(self.lines() - 1, 0)
        for indicator in (self.ERROR_INDICATOR, self.WARNING_INDICATOR):
            self.clearIndicatorRange(0, 0, last, self.lineLength(last), indicator)
        for marker in (self.ERROR_MARKER, self.WARNING_MARKER, self.ERROR_LINE_MARKER):
            self.markerDeleteAll(marker)

    def _diagnosticsAt(self, line: int) -> list[Diagnostic]:
        """Return the diagnostics on a line from 0, following the lines that moved since the run"""
        return [diagnostic for handle, diagnostic in self._diagnostics if self.markerLine(handle) == line]

    def _dropEditedDiagnostics(self):
        """Remove the diagnostics of the line being edited, since its error may be fixed"""
        if not self._diagnostics:
            return
        line, _ = self.getCursorPosition()
        kept = [(h, d) for h, d in self._diagnostics if self.markerLine(h) not in (line, -1)]
        if len(kept) == len(self._diagnostics):
            return
        self._diagnostics = kept
        self.clearIndicatorRange(line, 0, line, self.lineLength(line), self.ERROR_INDICATOR)
        self.clearIndicatorRange(line, 0, line, self.lineLength(line), self.WARNING_INDICATOR)
        for marker in (self.ERROR_MARKER, self.WARNING_MARKER, self.ERROR_LINE_MARKER):
            self.markerDelete(line, marker)

    def _showDiagnosticTooltip(self, position: int, x: int, y: int):
        """Show the messages of a line when the mouse rests on its marker or on an underlined token"""
        if not self._diagnostics:
            return
        in_margin = x < sum(self.marginWidth(m) for m in range(3))
        if position < 0 and not in_margin:
            return
        if not in_margin and not any(
                self.SendScintilla(QsciScintilla.SCI_INDICATORVALUEAT, i, position)
                for i in (self.ERROR_INDICATOR, self.WARNING_INDICATOR)):
            return
        point = self.SendScintilla(QsciScintilla.SCI_POSITIONFROMPOINT, x, y)
        messages = [d.message for d in self._diagnosticsAt(self.SendScintilla(QsciScintilla.SCI_LINEFROMPOSITION, point))]
        if messages:
            QToolTip.showText(self.viewport().mapToGlobal(QPoint(x, y)), "\n".join(messages), self)

    def _setupCompletion(self):
        """Keep the completion list up to date with the symbols of the file and silent inside comments"""
        self._completion_timer = QTimer(self)
        self._completion_timer.setSingleShot(True)
        self._completion_timer.setInterval(self.___COMPLETION_DELAY_MS)
        self._completion_timer.timeout.connect(self._refreshCompletions)
        self.textChanged.connect(self._completion_timer.start)
        self.SCN_CHARADDED.connect(self._cancelCompletionInComment)

    def _refreshCompletions(self):
        lexer = self.lexer()
        if hasattr(lexer, "refreshCompletions"):
            lexer.refreshCompletions(self.text())

    def _cancelCompletionInComment(self, _char: int):
        """Close the completion list opened while typing a comment or a string"""
        lexer = self.lexer()
        if not hasattr(lexer, "isInComment") or not self.isListActive():
            return
        line, index = self.getCursorPosition()
        if lexer.isInComment(self.text(line)[:index]):
            self.cancelList()

    def setText(self, text: str):
        """Replace the text, dropping the diagnostics that referred to the old one"""
        self.clearDiagnostics()
        super().setText(text)

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
        """Handle the zoom keys, the Find shortcut and the line cut and copy"""
        if handleZoomEvent(self, event, self.zoomIn, self._resetZoom):
            return
        if event.matches(QKeySequence.Find) or (
                event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_F):
            EventRegister.send(FindShortcutEvent(False), "editor/find")
            event.ignore()
            return
        # Cut and copy act on the selection, or on the whole line when nothing is selected.
        if not self.hasSelectedText():
            if event.matches(QKeySequence.Cut):
                self.SendScintilla(QsciScintilla.SCI_LINECUT)
                return
            if event.matches(QKeySequence.Copy):
                self.SendScintilla(QsciScintilla.SCI_LINECOPY)
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
