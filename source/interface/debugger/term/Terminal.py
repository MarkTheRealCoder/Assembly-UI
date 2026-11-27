import re

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QTextCursor, QKeySequence, QTextFrameFormat, QTextLength, \
    QTextBlockFormat, QFontMetricsF, QFontInfo
from PyQt5.QtWidgets import QTextEdit, QAction, QMenu

from source.comms.events import FindShortcutEvent
from source.comms.handlers import EventRegister
from source.interface import Settings, handleZoomEvent
from source.interface.templates import Tooltip


class TerminalGraphics(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setObjectName("Terminal")
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setAcceptRichText(False)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        self.tooltip = Tooltip(self, "This context is read-only.")
        self.tooltip.setPosition("above", "end")
        self.tooltip.setFollowing("mouse")
        self.tooltip.setAutomatic(False)


class TerminalLogic(TerminalGraphics):
    READONLY_STATE = 1
    READONLY_AND_MODIFIABLE_STATE = 2

    INFO_TAG = "[INFO]"
    WARNING_TAG = "[WARNING]"
    EXCEPTION_TAG = "[EXCEPTION]"

    # Distance between two baselines, in multiples of the font size (CSS line-height).
    LINE_HEIGHT = 1.2

    infoFmt = QTextCharFormat()
    infoTagFmt = QTextCharFormat()
    warnTagFmt = QTextCharFormat()
    errorTagFmt = QTextCharFormat()
    messageFmt = QTextCharFormat()
    writeFmt = QTextCharFormat()
    separatorFmt = QTextFrameFormat()
    messageBlockFmt = QTextBlockFormat()
    highlightFmt = QTextCharFormat()
    currentHighlightFmt = QTextCharFormat()

    # The family and size come from the stylesheet, so zoom can change the document font.
    for fmt in [infoFmt, infoTagFmt, warnTagFmt, errorTagFmt, messageFmt, writeFmt, highlightFmt, currentHighlightFmt]:
        fmt.setFontItalic(False)

    infoFmt.setForeground(QColor("#FFFFFF"))      # White: program output and the prompt
    infoTagFmt.setForeground(QColor("#4FC3F7"))   # Light blue: [INFO]
    warnTagFmt.setForeground(QColor("#E5C07B"))   # Yellow: [WARNING]
    errorTagFmt.setForeground(QColor("#F14C4C"))  # Red: [EXCEPTION]
    messageFmt.setForeground(QColor("#C8C8C8"))   # Light gray: text of a message
    writeFmt.setForeground(QColor("#00CC00"))     # Green: user input
    for fmt in [infoTagFmt, warnTagFmt, errorTagFmt]:
        fmt.setFontWeight(QFont.Bold)

    # Space above and below each message line, so consecutive messages stay apart.
    messageBlockFmt.setTopMargin(1)
    messageBlockFmt.setBottomMargin(1)
    highlightFmt.setBackground(QColor("#8800CC"))  # Purple highlight
    currentHighlightFmt.setBackground(QColor("#CC00FF"))  # Brighter purple for current match

    separatorFmt.setHeight(1)
    separatorFmt.setWidth(QTextLength(QTextLength.PercentageLength, 100))
    separatorFmt.setBorder(0)
    separatorFmt.setBackground(Qt.white)


    def __init__(self, parent):
        super().__init__(parent)
        self.setUndoRedoEnabled(False)
        self.separator()

        self._search_matches: list[tuple[int, int]] = []  # (start, end) positions
        self._current_match_index: int = -1
        self._base_font = None
        self._input_callback = None
        self._output_open: bool = False

    def beginProgram(self, input_callback: callable) -> None:
        """Prepare the terminal for a program and route submitted lines to the callback."""
        self._clearUserInput()
        self._input_callback = input_callback
        self._output_open = False

    def endProgram(self) -> None:
        """Close the program output and restore the normal terminal input."""
        self._clearUserInput()
        self._input_callback = None
        self._output_open = False

    def writeProgram(self, text: str) -> None:
        """Append program output above the line that the user is typing."""
        if not text:
            return
        bar = self.verticalScrollBar()
        follow = bar.value() >= bar.maximum()
        last = self.document().lastBlock()
        cursor = QTextCursor(self.document())

        if self._output_open:
            cursor.setPosition(last.position() - 1)
        else:
            cursor.setPosition(last.position())
            cursor.insertBlock()
            cursor.movePosition(QTextCursor.PreviousBlock)
            self._output_open = True

        first_block = cursor.blockNumber()
        cursor.setCharFormat(TerminalLogic.infoFmt)
        cursor.insertText(text)

        block = self.document().findBlockByNumber(first_block)
        input_block = self.document().lastBlock()
        while block.isValid() and block != input_block:
            block.setUserState(TerminalLogic.READONLY_STATE)
            self._setLineHeight(QTextCursor(block))
            block = block.next()
        input_block.setUserState(-1)

        if follow:
            bar.setValue(bar.maximum())

    def submitInput(self) -> None:
        """Move the typed lines into the read-only output and send them to the program."""
        lines = self._takeUserInput()
        if not lines:
            return
        self._write("\n".join(lines), TerminalLogic.writeFmt)
        self._input_callback(lines)

    def _takeUserInput(self) -> list[str]:
        """Remove the editable text at the end of the document and return its lines."""
        block = self.document().lastBlock()
        while block.previous().isValid() and not self.is_block_protected(block.previous()):
            block = block.previous()
        cursor = QTextCursor(self.document())
        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.End, QTextCursor.KeepAnchor)
        text = cursor.selectedText().replace(" ", "\n")
        cursor.removeSelectedText()
        self._resetCursor()
        return [line for line in text.split("\n") if line]

    def _clearUserInput(self) -> None:
        """Delete the text typed after the last protected block."""
        self._takeUserInput()

    @staticmethod
    def _fontSize(font: QFont) -> float:
        return font.pixelSize() if font.pixelSize() > 0 else font.pointSizeF()

    def zoomLevel(self) -> int:
        """Return the zoom steps applied to the font of the style sheet"""
        if self._base_font is None:
            return 0
        return round(self._fontSize(self.document().defaultFont()) - self._fontSize(self._base_font))

    def _zoomBy(self, steps: int):
        self.ensurePolished()
        document = self.document()
        if self._base_font is None:
            self._base_font = QFont(document.defaultFont())
        font = QFont(document.defaultFont())
        if font.pixelSize() > 0:
            font.setPixelSize(max(5, min(64, font.pixelSize() + steps)))
        else:
            font.setPointSizeF(max(5, min(64, font.pointSizeF() + steps)))
        document.setDefaultFont(font)

    def _resetZoom(self):
        if self._base_font is not None:
            self.document().setDefaultFont(self._base_font)

    def _set_to_eof(self):
        cursor = self.textCursor()
        if not cursor.atEnd():
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
        return cursor

    def _writeMessage(self, tag: str, tag_fmt: QTextCharFormat, text: str) -> None:
        """Write a message with a colored tag on each line and the text in light gray."""
        segments = []
        for line in str(text).splitlines() or [""]:
            segments.append((tag, tag_fmt))
            segments.append((f" {line}\n", TerminalLogic.messageFmt))
        self._writeSegments(segments, TerminalLogic.messageBlockFmt)

    def _writeSegments(self, segments: list[tuple[str, QTextCharFormat]], block_fmt: QTextBlockFormat = None,
                       userState = READONLY_STATE) -> None:
        """Append text segments with their formats at the end and protect their blocks."""
        cursor = self._set_to_eof()
        self._output_open = False
        block_start = cursor.position()

        for text, fmt in segments:
            cursor.insertText(text, fmt)

        last_pos = cursor.position() - 1
        cursor.setPosition(block_start)
        while cursor.position() <= last_pos:
            cursor.block().setUserState(userState)
            self._setLineHeight(cursor, block_fmt)
            if not cursor.movePosition(QTextCursor.NextBlock):
                break

        self._resetCursor()

    def _write(self, content: str or QTextFrameFormat, fmt: QTextCharFormat = None, userState = READONLY_STATE, keepPos = False) -> None:
        cursor = self._set_to_eof() if not keepPos else self.textCursor()
        self._output_open = False

        block_start = cursor.position()

        if fmt:
            cursor.setCharFormat(fmt)
            cursor.insertText((content + "\n") if not content.endswith("\n") else content)

        else:
            cursor.insertFrame(content)

        last_pos = cursor.position() - 1
        cursor.setPosition(block_start)
        while cursor.position() <= last_pos:
            cursor.block().setUserState(userState)  # 1 = read-only | 2 = read-only but can be modified by code
            self._setLineHeight(cursor)
            if not cursor.movePosition(QTextCursor.NextBlock):
                cursor.movePosition(QTextCursor.EndOfBlock)

        self._resetCursor()

    def _lineHeightPercent(self) -> float:
        """Line height as a percentage of the font's own line spacing, which is what Qt expects"""
        self.ensurePolished()
        font = self.document().defaultFont()
        spacing = QFontMetricsF(font).lineSpacing()
        if spacing <= 0:
            return 100.0
        return max(80.0, 100.0 * TerminalLogic.LINE_HEIGHT * QFontInfo(font).pixelSize() / spacing)

    def _setLineHeight(self, cursor: QTextCursor, block_fmt: QTextBlockFormat = None) -> None:
        """Give the block under the cursor the terminal line height, merged with block_fmt if given"""
        fmt = QTextBlockFormat(block_fmt) if block_fmt is not None else cursor.blockFormat()
        fmt.setLineHeight(self._lineHeightPercent(), QTextBlockFormat.ProportionalHeight)
        cursor.setBlockFormat(fmt)

    def _resetCursor(self) -> None:
        cursor = self._set_to_eof()
        cursor.setCharFormat(TerminalLogic.writeFmt)
        self.setTextCursor(cursor)

    def is_block_protected(self, block):
        """Check if a block is protected"""
        return block.isValid() and (block.userState() == TerminalLogic.READONLY_STATE or block.userState() == TerminalLogic.READONLY_AND_MODIFIABLE_STATE)

    def selection_includes_protected(self):
        """Check if current selection includes any protected blocks"""
        cursor = self.textCursor()
        if not cursor.hasSelection():
            return False

        start = cursor.selectionStart()
        end = cursor.selectionEnd()

        check_cursor = self.textCursor()
        check_cursor.setPosition(start)

        while check_cursor.position() < end:
            if self.is_block_protected(check_cursor.block()):
                return True
            if not check_cursor.movePosition(QTextCursor.NextBlock):
                break

        return False

    def info(self, text: str) -> None:
        self._writeMessage(TerminalLogic.INFO_TAG, TerminalLogic.infoTagFmt, text)

    def warning(self, text: str) -> None:
        self._writeMessage(TerminalLogic.WARNING_TAG, TerminalLogic.warnTagFmt, text)

    def error(self, text: str) -> None:
        self._writeMessage(TerminalLogic.EXCEPTION_TAG, TerminalLogic.errorTagFmt, text)

    def separator(self) -> None:
        self._write(TerminalLogic.separatorFmt)

    def prompt(self) -> None:
        """Write the separator bar and the prompt of the current file, as at the start of the terminal."""
        self.separator()
        document = Settings.get("editor/current", None)
        if document:
            self.writeModifiable(f"{document} >>")
        self.scrollDown()

    def writeModifiable(self, text: str) -> None:
        keepPos = False
        if blocks := self._findLastModifiableBlocks():
            cursor = self.textCursor()
            cursor.setPosition(blocks[-1].position() + blocks[-1].length())
            cursor.setPosition(blocks[0].position(), QTextCursor.KeepAnchor)
            cursor.removeSelectedText()
            cursor.setPosition(blocks[0].position())
            self.setTextCursor(cursor)
            self._cursorSetPositionBeforeUserText()
            keepPos = True
        self._write(text, TerminalLogic.infoFmt, TerminalLogic.READONLY_AND_MODIFIABLE_STATE, keepPos)

    def _cursorSetPositionBeforeUserText(self):
        """Set cursor position before user-modifiable text"""
        block = self.document().lastBlock()
        cursor = self.textCursor()

        while block.isValid():
            if block.userState() == 0:
                b = block.previous()
                if b.isValid() and b.userState() == 0:
                    block = b
                else:
                    break
            else:
                break

        cursor.setPosition(block.position())
        cursor.movePosition(QTextCursor.StartOfBlock)
        self.setTextCursor(cursor)

    def _findLastModifiableBlocks(self):
        """Find the last contiguous blocks that are modifiable by code"""
        block = self.document().lastBlock()
        modifiable_blocks = []

        while block.isValid():
            if block.userState() == TerminalLogic.READONLY_AND_MODIFIABLE_STATE:
                modifiable_blocks.append(block)
            elif block.userState() == TerminalLogic.READONLY_STATE:
                break

            block = block.previous()

        return list(reversed(modifiable_blocks)) if modifiable_blocks else None

    def clear(self) -> None:
        self.setText("")
        self._output_open = False
        self.separator()
        if Settings.get("editor/current", None):
            document = Settings.get("editor/current", None)
            self.writeModifiable(f"{document} >>")
        cursor = self.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.setTextCursor(cursor)

    def scrollDown(self):
        self.moveCursor(self.textCursor().End)

    def scrollUp(self):
        self.moveCursor(self.textCursor().Start)

    def openFindWidget(self):
        EventRegister.send(FindShortcutEvent(False), "terminal/find")

    def paste(self):
        cursor = self.textCursor()
        current_block = cursor.block()
        if self.is_block_protected(current_block) or self.selection_includes_protected():
            cursor.movePosition(QTextCursor.End)
        cursor.setCharFormat(TerminalLogic.writeFmt)
        self.setTextCursor(cursor)
        super().paste()
    
    def _clearHighlights(self):
        """Remove all search highlights from the document."""
        cursor = QTextCursor(self.document())
        cursor.select(QTextCursor.Document)
        
        # Reset to default format (preserves original formatting)
        fmt = QTextCharFormat()
        fmt.setBackground(QColor("transparent"))
        cursor.mergeCharFormat(fmt)

    def _highlightMatches(self):
        """Highlight all search matches."""
        self._clearHighlights()
        
        for i, (start, end) in enumerate(self._search_matches):
            cursor = QTextCursor(self.document())
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            
            if i == self._current_match_index:
                cursor.mergeCharFormat(TerminalLogic.currentHighlightFmt)
            else:
                cursor.mergeCharFormat(TerminalLogic.highlightFmt)

    def _performSearch(self, prompt: str, use_regex: bool) -> int:
        """Search for text in terminal content. Returns number of matches."""
        self._search_matches.clear()
        self._current_match_index = -1
        
        if not prompt:
            self._clearHighlights()
            return 0
        
        text = self.toPlainText()
        
        try:
            if use_regex:
                pattern = re.compile(prompt)
                for match in pattern.finditer(text):
                    self._search_matches.append((match.start(), match.end()))
            else:
                lower_text = text.lower()
                lower_prompt = prompt.lower()
                start = 0
                while True:
                    pos = lower_text.find(lower_prompt, start)
                    if pos == -1:
                        break
                    self._search_matches.append((pos, pos + len(prompt)))
                    start = pos + 1
        except re.error:
            # Invalid regex - treat as literal
            return 0
        
        if self._search_matches:
            self._current_match_index = 0
            self._highlightMatches()
            self._scrollToCurrentMatch()
        
        return len(self._search_matches)

    def _scrollToCurrentMatch(self):
        """Scroll to and select the current match."""
        if 0 <= self._current_match_index < len(self._search_matches):
            start, end = self._search_matches[self._current_match_index]
            cursor = QTextCursor(self.document())
            cursor.setPosition(start)
            cursor.setPosition(end, QTextCursor.KeepAnchor)
            self.setTextCursor(cursor)
            self.ensureCursorVisible()

    def _navigateMatch(self, direction: str):
        """Navigate to next or previous match."""
        if not self._search_matches:
            return
        
        if direction == "next":
            self._current_match_index = (self._current_match_index + 1) % len(self._search_matches)
        elif direction == "prev":
            self._current_match_index = (self._current_match_index - 1) % len(self._search_matches)
        
        self._highlightMatches()
        self._scrollToCurrentMatch()

    def _getOccurrenceInfo(self) -> tuple[int, int]:
        """Returns (current_index + 1, total_matches) for display."""
        if not self._search_matches:
            return (0, 0)
        return (self._current_match_index + 1, len(self._search_matches))


@EventRegister.register(FindShortcutEvent, "terminal")
class Terminal(TerminalLogic):
    def __init__(self, parent):
        super().__init__(parent)
        Settings.addNotificationGroup("editor/current", self.onChangeDocument)

        # The action belongs to the terminal, so its shortcuts work while the terminal has focus.
        self._clear_action = QAction("Clear Terminal", self)
        self._clear_action.setShortcuts([QKeySequence(Qt.CTRL + Qt.Key_L), QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_K)])
        self._clear_action.setShortcutContext(Qt.WidgetWithChildrenShortcut)
        self._clear_action.triggered.connect(self.clear)
        self.addAction(self._clear_action)

        # The zoom of the last session waits for the first show, when the style sheet has set the font.
        self._pending_zoom: int = Settings.get("terminal/zoom", 0, int)

    def showEvent(self, event):
        super().showEvent(event)
        if self._pending_zoom:
            self._zoomBy(self._pending_zoom)
        self._pending_zoom = 0

    def zoomLevel(self) -> int:
        return self._pending_zoom or super().zoomLevel()

    def onFindShortcutEvent(self, event: FindShortcutEvent):
        """Handle find events from the FindWidget."""
        if event.mustClose():
            self._clearHighlights()
            self._resetCursor()
            self._search_matches.clear()
            self._current_match_index = -1
            return
        
        movement = event.getMovement()
        prompt = event.getPrompt()
        
        if movement != "none":
            self._navigateMatch(movement)
        elif prompt is not None:
            self._clearHighlights()
            self._resetCursor()
            self._current_match_index = -1
            self._performSearch(prompt, event.isRegex())
        
        EventRegister.send(
            FindShortcutEvent(
                False,
                occurrencies=self._getOccurrenceInfo()
            ),
            "terminal/find"
        )

    def onChangeDocument(self):
        if self._input_callback is not None:
            return
        document = Settings.get("editor/current", None)
        if document:
            self.writeModifiable(f"{document} >>")

    def viewportEvent(self, event):
        if handleZoomEvent(self, event, self._zoomBy, self._resetZoom):
            return True
        return super().viewportEvent(event)

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        for text, shortcut, slot in (("Paste", QKeySequence.Paste, self.paste), ("Copy", QKeySequence.Copy, self.copy)):
            action = QAction(text, menu)
            action.setShortcut(shortcut)
            action.triggered.connect(slot)
            menu.addAction(action)
        menu.addSeparator()
        select_all = QAction("Select All", menu)
        select_all.setShortcut(QKeySequence.SelectAll)
        select_all.triggered.connect(self.selectAll)
        menu.addAction(select_all)
        menu.addSeparator()
        menu.addAction(self._clear_action)
        menu.exec_(e.globalPos())
        menu.deleteLater()

    def keyPressEvent(self, event):
        """Prevent editing read-only blocks"""
        if handleZoomEvent(self, event, self._zoomBy, self._resetZoom):
            return

        cursor = self.textCursor()
        current_block = cursor.block()

        if self.tooltip.isShown():
            self.tooltip.hideTooltip()

        if self._input_callback is not None and event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.submitInput()
            event.accept()
            return

        if event.key() == Qt.Key_Backspace:
            if not self.backspaceEvent(cursor, current_block):
                event.ignore()
                return

        elif event.key() == Qt.Key_Delete:
            if not self.deleteEvent(cursor, current_block):
                event.ignore()
                return

        elif event.text() and not event.modifiers() & (Qt.ControlModifier | Qt.AltModifier):
            if self.is_block_protected(current_block) or self.selection_includes_protected():
                event.ignore()
                return
            else:
                cursor.setCharFormat(TerminalLogic.writeFmt)
                self.setTextCursor(cursor)

        elif event.matches(QKeySequence.Cut) or (event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_X):
            self.tooltip.showTooltip()
            event.ignore()
            return

        elif event.matches(QKeySequence.Paste) or (
                event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_V):
            self.paste()
            event.ignore()
            return

        elif event.matches(QKeySequence.Find) or (
                event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_F):
            self.openFindWidget()
            event.ignore()
            return

        super().keyPressEvent(event)

    def backspaceEvent(self, cursor, current_block):
        if cursor.hasSelection():
            if self.selection_includes_protected():
                return False
        else:
            if cursor.atBlockStart():
                # At start of block - would delete from previous block
                prev_block = current_block.previous()
                if self.is_block_protected(prev_block):
                    return False
            elif self.is_block_protected(current_block):
                return False
        return True

    def deleteEvent(self, cursor, current_block):
        if cursor.hasSelection():
            if self.selection_includes_protected():
                return False
        else:
            if cursor.atBlockEnd() and self.is_block_protected(current_block):
                # Would delete from next block - block this
                return False
            elif self.is_block_protected(current_block):
                return False
        return True

