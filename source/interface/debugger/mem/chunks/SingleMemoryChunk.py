from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QLabel, QApplication

from source.filesystem import find_path
from source.interface.shared import createLayout
from source.interface.templates import GenericButton, Tooltip


class _CopyButton(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional UI setup can be done here
        self.setIcon(self.rerenderIcon(QIcon(find_path("copy.svg")), "#6b6b6b"))
        self.setIconSize(QSize(16, 16))
        self.___tooltip = Tooltip(self, "Copied to clipboard")
        self.___tooltip.setFollowing("widget")
        self.___tooltip.setPosition("below", "center")
        self.___tooltip.setAutomatic(False)

        self.clicked.connect(self.___tooltip.showTooltip)


class SingleMemoryChunkGraphics(QFrame):
    #_CHUNK_TYPES = {list: "dict", type(None): "function"}

    def __init__(self, parent, key: str, value: str or int ): #or list[tuple[str, int]] or None = None
        super().__init__(parent)
        self.setObjectName("SingleMemoryChunk")
        # Additional UI setup can be done here
        #_type = self._CHUNK_TYPES.get(type(value), "default")
        #self.setProperty("chunk_type", _type)
        #layout = createLayout(QHBoxLayout, self) if _type == "default" else createLayout(QVBoxLayout, self)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        _key = QLabel(f"{key}:")
        _key.setObjectName("MemoryChunkKey")
        _key.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        layout.addWidget(_key, 1)
        _value = QLabel(value if isinstance(value, str) else hex(value))
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
        # Implementation of memory chunk logic goes here
        button: _CopyButton = self.layout().itemAt(2).widget()
        button.clicked.connect(self.copyToClipboard)

    def getKey(self) -> str:
        return self._key

    def getValue(self) -> str or int:
        return self._value

    def setValue(self, value: str or int):
        self._value = value
        # Update the UI representation of the value if necessary
        value_label: QLabel = self.layout().itemAt(1).widget()
        value_label.setText(value if isinstance(value, str) else hex(value))

    def copyToClipboard(self):
        clipboard = QApplication.clipboard()
        clipboard.setText(f"{self._key}: {self._value}" if isinstance(self._value, str) else f"{self._key}: {hex(self._value)}")


class SingleMemoryChunk(SingleMemoryChunkLogic):
    def __init__(self, parent, key: str, value: str or int or None = None):
        super().__init__(parent, key, value)
        # Additional initialization for chunks