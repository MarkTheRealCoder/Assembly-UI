from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel

from source.interface.debugger.mem.ColoredDrop import ColoredDrop
from source.interface.shared import createLayout
from source.platform import roundColors


class CompoundMemoryChunkHeader(QFrame):
    def __init__(self, name: str, color: str = "red"):
        super().__init__()
        self.setObjectName("ContextHeader")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(ColoredDrop(self, 6, color, shape="circle"))
        layout.addSpacing(10)

        label = QLabel(name)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setFixedHeight(label.fontMetrics().ascent() + 2)
        label.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(label)
        self.setLayout(layout)


class CompoundMemoryChunkGraphics(QFrame):
    def __init__(self, parent, name: str, color: str = None):
        super().__init__(parent)
        self.setObjectName("CompoundMemoryChunk")
        # Additional UI setup can be done here
        color = roundColors('Compound') if color is None else color
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setStyleSheet(f"QFrame#CompoundMemoryChunk {{ border-left: 1px solid {color}; }}")
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(CompoundMemoryChunkHeader(name, color=color), 1)
        inner_layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        inner_layout.setContentsMargins(8, 8, 8, 8)
        inner_layout.setSpacing(4)
        layout.addLayout(inner_layout, 2)
        self.setLayout(layout)


class CompoundMemoryChunkLogic(CompoundMemoryChunkGraphics):
    def __init__(self, parent, name: str, color: str):
        super().__init__(parent, name, color)
        # Implementation of compound memory chunk logic goes here
        self._key = name

    def getKey(self) -> str:
        return self._key


class CompoundMemoryChunk(CompoundMemoryChunkLogic):
    def __init__(self, parent, name: str, color: str = None):
        super().__init__(parent, name, roundColors(name) if color is None else color)
        # Additional initialization for CompoundMemoryChunk

