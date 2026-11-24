from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QHBoxLayout, QLabel, QApplication, QSizePolicy

from source.filesystem import find_path
from source.interface.debugger.mem.chunks.MemoryChunk import _MemoryChunk
from source.interface.shared import createLayout
from source.interface.templates import GenericButton, Tooltip


class _CopyButton(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(self.rerenderIcon(QIcon(find_path("copy.svg")), "#6b6b6b"))
        self.setIconSize(QSize(16, 16))
        self.___tooltip = Tooltip(self, "Copied to clipboard")
        self.___tooltip.setFollowing("widget")
        self.___tooltip.setPosition("below", "center")
        self.___tooltip.setAutomatic(False)

        self.clicked.connect(self.___tooltip.showTooltip)


class SingleMemoryChunkGraphics(_MemoryChunk):
    # Display base shared by every chunk: 16, 10 or 8.
    base: int = 16
    ___FORMATS = {16: hex, 10: str, 8: oct}

    @staticmethod
    def formatValue(value: str or int) -> str:
        """ Text of a value in the current display base. Text values are shown as they are. """
        if isinstance(value, str):
            return value
        return SingleMemoryChunkGraphics.___FORMATS[SingleMemoryChunkGraphics.base](value)

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
        layout.addWidget(_CopyButton(self), 0)
        self.setLayout(layout)


class SingleMemoryChunkLogic(SingleMemoryChunkGraphics):
    def __init__(self, parent, key: str, value: str or int or None = None):
        super().__init__(parent, key, value)
        self._value = value
        self._key = key
        button: _CopyButton = self.layout().itemAt(2).widget()
        button.clicked.connect(self.copyToClipboard)

    def getKey(self) -> str:
        return self._key

    def getValue(self) -> str or int:
        return self._value

    def setValue(self, value: str or int):
        self._value = value
        self.refresh()

    def refresh(self):
        """ Show the value again in the current display base """
        value_label: QLabel = self.layout().itemAt(1).widget()
        value_label.setText(self.formatValue(self._value))
        self.updated()

    def copyToClipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(f"{self._key}: {self.formatValue(self._value)}")


class SingleMemoryChunk(SingleMemoryChunkLogic):
    def __init__(self, parent, key: str, value: str or int or None = None):
        super().__init__(parent, key, value)
