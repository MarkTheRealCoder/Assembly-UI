from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel

from source.interface.debugger.mem.ColoredDrop import ColoredDrop
from source.interface.debugger.mem.chunks import MemoryChunk, CompoundMemoryChunk, SingleMemoryChunk
from source.interface.shared import createLayout
from source.platform import roundColors


class ContextHeader(QFrame):
    def __init__(self, name: str, color: str = "red"):
        super().__init__()
        self.setObjectName("ContextHeader")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)
        layout.addWidget(ColoredDrop(self, 6, color, shape="rounded-square"))
        layout.addSpacing(10)

        label = QLabel(name)
        label.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        label.setFixedHeight(label.fontMetrics().ascent() + 2)
        label.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(label)
        self.setLayout(layout)


class ContextWindowGraphics(QFrame):
    def __init__(self, parent, name: str):
        super().__init__(parent)
        self.setObjectName("ContextWindow")
        # Additional UI setup can be done here
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(ContextHeader(name.upper(), color=roundColors("CONTEXTS")), 1)
        inner_layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        inner_layout.setContentsMargins(8, 8, 8, 8)
        inner_layout.setSpacing(4)
        layout.addLayout(inner_layout, 2)
        self.setLayout(layout)


class ContextWindowLogic(ContextWindowGraphics):
    @staticmethod
    def findByNodeKey(c, key: str) -> CompoundMemoryChunk or SingleMemoryChunk or None:
        current_layout: QVBoxLayout = c.layout().findChild(QVBoxLayout)
        for i in range(current_layout.count()):
            widget = current_layout.itemAt(i).widget()
            if widget.getKey() == key:
                return widget
        return None

    @staticmethod
    def recursive_node_path(c: CompoundMemoryChunk, path: list[str], value: str or int or None, color_section: str = None):
        if len(path) == 0:
            return
        current_layout: QVBoxLayout = c.layout().findChild(QVBoxLayout)
        child = ContextWindowLogic.findByNodeKey(c, path[0])
        if child is None:
            child = MemoryChunk(c, path[0], value, color_section)
            current_layout.addWidget(child)
            ContextWindowLogic.recursive_node_path(child, path[1:], value, color_section)
        elif len(path) == 1:
            if isinstance(child, SingleMemoryChunk):
                child.setValue(value)
        else:
            ContextWindowLogic.recursive_node_path(child, path[1:], value, color_section)

    @staticmethod
    def removeNodeRecursive(c: CompoundMemoryChunk, path: list[str]):
        if len(path) == 0:
            return
        current_layout: QVBoxLayout = c.layout().findChild(QVBoxLayout)
        child = ContextWindowLogic.findByNodeKey(c, path[0])
        if child is not None:
            if len(path) == 1:
                current_layout.removeWidget(child)
                child.deleteLater()
            else:
                ContextWindowLogic.removeNodeRecursive(child, path[1:])


    def __init__(self, parent, name: str):
        super().__init__(parent, name)
        # Implementation of context window logic goes here

    def addNewNode(self, node_path: str, node_value: str or int or None = None):
        # Logic to add a new node to the context window
        _path_members = node_path.split(".")
        current_layout: QVBoxLayout = self.layout().findChild(QVBoxLayout)
        child = ContextWindowLogic.findByNodeKey(self, _path_members[0])
        if child is None:
            child = MemoryChunk(self, _path_members[0], node_value, _path_members[0])
            current_layout.addWidget(child)
            ContextWindowLogic.recursive_node_path(child, _path_members[1:], node_value, _path_members[0])
        elif len(_path_members) == 1:
            if isinstance(child, SingleMemoryChunk):
                child.setValue(node_value)
        else:
            ContextWindowLogic.recursive_node_path(child, _path_members[1:], node_value, _path_members[0])

    def clearNodes(self):
        current_layout: QVBoxLayout = self.layout().findChild(QVBoxLayout)
        while current_layout.count() > 0:
            item = current_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def removeNode(self, node_path: str):
        _path_members = node_path.split(".")
        current_layout: QVBoxLayout = self.layout().findChild(QVBoxLayout)
        child = ContextWindowLogic.findByNodeKey(self, _path_members[0])
        if child is not None:
            if len(_path_members) == 1:
                current_layout.removeWidget(child)
                child.deleteLater()
            else:
                ContextWindowLogic.removeNodeRecursive(child, _path_members[1:])

    def popLastNode(self):
        # todo Better to update it to pop the last node inside a CompoundMemoryChunk instead of the last node of the context window
        current_layout: QVBoxLayout = self.layout().findChild(QVBoxLayout)
        lc = current_layout.count()
        if lc > 0:
            item = current_layout.takeAt(lc - 1)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()


class ContextWindow(ContextWindowLogic):
    def __init__(self, parent, name: str):
        super().__init__(parent, name)
        # Additional initialization for ContextWindow