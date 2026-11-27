from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QApplication, QSizePolicy

from source.filesystem import find_path
from source.interface import createLayout
from source.interface.debugger.mem.chunks.MemoryChunk import _MemoryChunk
from source.interface.templates import GenericButton, Tooltip


class _CharacterButton(GenericButton):
    """ Toggle between the number of the value and the ASCII character it encodes """
    ___ICON_COLOR = "#6b6b6b"
    ___ACTIVE_ICON_COLOR = "#569CD6"

    def __init__(self, parent):
        super().__init__(parent)
        self.setCheckable(True)
        self.setIconSize(QSize(16, 16))
        self.___icon = QIcon(find_path("ascii.svg"))
        self.___tooltip = Tooltip(self, "")
        self.___tooltip.setFollowing("widget")
        self.___tooltip.setPosition("below", "center")
        self.___tooltip.setAutomatic(True)
        self.toggled.connect(self.___showState)
        self.___showState(False)
        # A hidden button keeps its space, so the values stay aligned with the chunks that have one.
        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(policy)

    def ___showState(self, checked: bool):
        color = self.___ACTIVE_ICON_COLOR if checked else self.___ICON_COLOR
        self.setIcon(self.rerenderIcon(self.___icon, color))
        self.___tooltip.setText("Show as number" if checked else "Show as ASCII character")


class SingleMemoryChunkGraphics(_MemoryChunk):
    # Display base shared by every chunk: 16, 10 or 8.
    base: int = 16
    ___FORMATS = {16: hex, 10: str, 8: oct}
    # ASCII codes shown as characters: the space up to the tilde, plus tab and newline.
    ___FIRST_VISIBLE = 0x20
    ___LAST_VISIBLE = 0x7E
    ___WHITESPACE = (0x09, 0x0A)

    @staticmethod
    def formatValue(value: str or int) -> str:
        """ Text of a value in the current display base. Text values are shown as they are. """
        if isinstance(value, str):
            return value
        return SingleMemoryChunkGraphics.___FORMATS[SingleMemoryChunkGraphics.base](value)

    @staticmethod
    def isCharacter(value: str or int) -> bool:
        """ Whether the value is the ASCII code of a visible character, the space, a tab or a newline """
        return isinstance(value, int) and (value in SingleMemoryChunkGraphics.___WHITESPACE
                                           or SingleMemoryChunkGraphics.___FIRST_VISIBLE <= value <= SingleMemoryChunkGraphics.___LAST_VISIBLE)

    @staticmethod
    def formatCharacter(value: str or int) -> str:
        """ Text of a value as its ASCII character, quoted: '\\t' and '\\n' are escaped, other values stay as they are """
        if not SingleMemoryChunkGraphics.isCharacter(value):
            return SingleMemoryChunkGraphics.formatValue(value)
        return repr(chr(value))

    @staticmethod
    def setNumberBase(base: int):
        """ Select the display base of every chunk: 16, 10 or 8. Call refresh on the existing chunks to apply it. """
        if base not in SingleMemoryChunkGraphics.___FORMATS:
            raise ValueError(f"Unsupported number base: {base}")
        SingleMemoryChunkGraphics.base = base

    def __init__(self, parent, key: str, value: str or int):
        super().__init__(parent)
        self.setObjectName("SingleMemoryChunk")
        # The chunk takes the height of its content; only the width follows the parent.
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        _key = QLabel(f"{key}:")
        _key.setObjectName("MemoryChunkKey")
        _key.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(_key, 1)
        _value = QLabel(SingleMemoryChunkGraphics.formatValue(value))
        _value.setObjectName("MemoryChunkValue")
        _value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        layout.addWidget(_value, 2)
        layout.addWidget(_CharacterButton(self), 0)
        self.setLayout(layout)


class SingleMemoryChunkLogic(SingleMemoryChunkGraphics):
    def __init__(self, parent, key: str, value: str or int or None = None):
        super().__init__(parent, key, value)
        self._value = value
        self._key = key
        self.___character: bool = False
        button: _CharacterButton = self.layout().itemAt(2).widget()
        button.toggled.connect(self.showCharacter)
        self.___updateCharacterButton()

    def getValue(self) -> str or int:
        return self._value

    def setValue(self, value: str or int):
        self._value = value
        self.___updateCharacterButton()
        self.refresh()

    def ___updateCharacterButton(self):
        """ Offer the character view only for the values that are a visible ASCII character, a tab or a newline """
        button: _CharacterButton = self.layout().itemAt(2).widget()
        convertible = self.isCharacter(self._value)
        if not convertible and button.isChecked():
            button.setChecked(False)
        button.setVisible(convertible)

    def displayText(self) -> str:
        """ Text of the value as it is shown: a number in the current base or an ASCII character """
        if self.___character:
            return self.formatCharacter(self._value)
        return self.formatValue(self._value)

    def showCharacter(self, enabled: bool):
        """ Show the value as the ASCII character of its code instead of a number """
        self.___character = enabled
        self.___showValue()

    def refresh(self):
        """ Show the value again in the current display base """
        self.___showValue()
        self.updated()

    def ___showValue(self):
        value_label: QLabel = self.layout().itemAt(1).widget()
        value_label.setText(self.displayText())

    def copyToClipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(f"{self._key}: {self.displayText()}")


class SingleMemoryChunk(SingleMemoryChunkLogic):
    def __init__(self, parent, key: str, value: str or int or None = None):
        super().__init__(parent, key, value)

    def mouseDoubleClickEvent(self, event):
        """ Copy the chunk to the clipboard and flash it in white """
        if event.button() == Qt.LeftButton:
            self.copyToClipboard()
            self.highlighted()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)
