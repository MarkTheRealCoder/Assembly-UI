from PyQt5.QtCore import Qt
from PyQt5.QtGui import QTextCharFormat, QColor, QFont, QTextCursor, QKeySequence, QTextFrameFormat, QTextLength
from PyQt5.QtWidgets import QTextEdit, QAction, QMenu

from source.comms.events.FindShortcut import FindShortcutEvent
from source.comms.handlers import EventRegister
from source.interface.shared import Settings
from source.interface.templates import Tooltip


class TerminalGraphics(QTextEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setReadOnly(False)
        self.setObjectName("Terminal")
        self.setLineWrapMode(QTextEdit.LineWrapMode.WidgetWidth)
        self.setAcceptRichText(False)

        self.tooltip = Tooltip(self, "This context is read-only.")
        self.tooltip.setPosition("above", "end")
        self.tooltip.setFollowing("mouse")
        self.tooltip.setAutomatic(False)



class TerminalLogic(TerminalGraphics):
    READONLY_STATE = 1
    READONLY_AND_MODIFIABLE_STATE = 2

    infoFmt = QTextCharFormat()
    warnFmt = QTextCharFormat()
    errorFmt = QTextCharFormat()
    writeFmt = QTextCharFormat()
    separatorFmt = QTextFrameFormat()

    for fmt in [infoFmt, warnFmt, errorFmt, writeFmt]:
        fmt.setFont(QFont("FiraCode"))
        fmt.setFontPointSize(13)
        fmt.setFontItalic(False)

    infoFmt.setForeground(QColor("#FFFFFF"))   # White
    warnFmt.setForeground(QColor("#CCCC00"))   # Yellow
    errorFmt.setForeground(QColor("#DD0000"))  # Red
    writeFmt.setForeground(QColor("#00CC00"))  # Green

    separatorFmt.setHeight(1)
    separatorFmt.setWidth(QTextLength(QTextLength.PercentageLength, 100))
    separatorFmt.setBorder(0)
    separatorFmt.setBackground(Qt.white)


    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of terminal logic goes here
        self.setUndoRedoEnabled(False)
        self.separator()

    def _set_to_eof(self):
        cursor = self.textCursor()
        if not cursor.atEnd():
            cursor.movePosition(cursor.MoveOperation.End)
            self.setTextCursor(cursor)
        return cursor

    def _write(self, content: str or QTextFrameFormat, fmt: QTextCharFormat = None, userState = READONLY_STATE, keepPos = False) -> None:
        cursor = self._set_to_eof() if not keepPos else self.textCursor()

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
            if not cursor.movePosition(QTextCursor.NextBlock):
                cursor.movePosition(QTextCursor.EndOfBlock)

        self._resetCursor()

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

        # Create a cursor to iterate through selection
        check_cursor = self.textCursor()
        check_cursor.setPosition(start)

        while check_cursor.position() < end:
            if self.is_block_protected(check_cursor.block()):
                return True
            if not check_cursor.movePosition(QTextCursor.NextBlock):
                break

        return False

    def info(self, text: str) -> None:
        self._write(f"[INFO]: {text}", TerminalLogic.infoFmt)

    def warning(self, text: str) -> None:
        self._write(text, TerminalLogic.warnFmt)

    def error(self, text: str) -> None:
        self._write(text, TerminalLogic.errorFmt)

    def separator(self) -> None:
        self._write(TerminalLogic.separatorFmt)

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
        EventRegister.send(FindShortcutEvent(), "terminal")

    def paste(self):
        cursor = self.textCursor()
        current_block = cursor.block()
        if self.is_block_protected(current_block) or self.selection_includes_protected():
            cursor.movePosition(QTextCursor.End)
        cursor.setCharFormat(TerminalLogic.writeFmt)
        self.setTextCursor(cursor)
        super().paste()


class Terminal(TerminalLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for Terminal
        Settings.addNotificationGroup("editor/current", self.onChangeDocument)

    def onChangeDocument(self):
        document = Settings.get("editor/current", None)
        if document:
            self.writeModifiable(f"{document} >>")

    def contextMenuEvent(self, e):
        menu = QMenu(self)
        for act in [

                ("Paste", [QKeySequence.Paste], self.paste),
                ("Copy", [QKeySequence.Copy], self.copy),
                "slash",
                ("Select All", [QKeySequence.SelectAll], self.selectAll),
                "slash",
                ("Clear Terminal", [QKeySequence(Qt.CTRL + Qt.Key_L), QKeySequence(Qt.CTRL + Qt.SHIFT + Qt.Key_K)], self.clear)
            ]:
            if act == "slash":
                menu.addSeparator()
                continue
            action = QAction(self)
            action.setText(act[0])
            if act[1]:
                action.setShortcuts(act[1])
            action.triggered.connect(act[2])
            menu.addAction(action)

        menu.exec_(e.globalPos())

    def keyPressEvent(self, event):
        """Prevent editing read-only blocks"""
        cursor = self.textCursor()
        current_block = cursor.block()

        if self.tooltip.isShown():
            self.tooltip.hideTooltip()

        # BACKSPACE key
        if event.key() == Qt.Key_Backspace:
            if not self.backspaceEvent(cursor, current_block):
                event.ignore()
                return

        # DELETE key
        elif event.key() == Qt.Key_Delete:
            if not self.deleteEvent(cursor, current_block):
                event.ignore()
                return

        # Regular typing
        elif event.text() and not event.modifiers() & (Qt.ControlModifier | Qt.AltModifier):
            if self.is_block_protected(current_block) or self.selection_includes_protected():
                event.ignore()
                return
            else:
                cursor.setCharFormat(TerminalLogic.writeFmt)
                self.setTextCursor(cursor)

        # CUT operation
        elif event.matches(QKeySequence.Cut) or (event.modifiers() & Qt.ControlModifier and event.key() == Qt.Key_X):
            self.tooltip.showTooltip()
            event.ignore()
            return

        # PASTE operation into protected block
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
            # Check if selection includes protected blocks
            if self.selection_includes_protected():
                return False
        else:
            # Check current position
            if cursor.atBlockStart():
                # At start of block - would delete from previous block
                prev_block = current_block.previous()
                if self.is_block_protected(prev_block):
                    return False
            elif self.is_block_protected(current_block):
                # Inside protected block
                return False
        return True

    def deleteEvent(self, cursor, current_block):
        if cursor.hasSelection():
            if self.selection_includes_protected():
                return False
        else:
            # Check if at end of protected block
            if cursor.atBlockEnd() and self.is_block_protected(current_block):
                # Would delete from next block - block this
                return False
            elif self.is_block_protected(current_block):
                # Inside protected block
                return False
        return True

# todo make find functionality to search text inside terminal and move cursor to its results
