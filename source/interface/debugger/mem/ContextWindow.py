from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout, QLabel

from source.interface.debugger.mem.ColoredDrop import ColoredDrop
from source.interface.debugger.mem.chunks import CompoundMemoryChunk, SingleMemoryChunk
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
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(ContextHeader(name.upper(), color=roundColors("CONTEXTS")), 1)
        inner_layout: QVBoxLayout = createLayout(QVBoxLayout)
        inner_layout.setContentsMargins(8, 8, 8, 8)
        inner_layout.setSpacing(4)
        layout.addLayout(inner_layout, 2)
        self.setLayout(layout)
        self._inner_layout = inner_layout


class ContextWindowLogic(ContextWindowGraphics):
    """ Tree of memory nodes. Each container indexes its children by key for constant-time updates. """

    @staticmethod
    def findByNodeKey(c, key: str) -> CompoundMemoryChunk or SingleMemoryChunk or None:
        """ Returns the direct child of a container with the given key. """
        return c.getNodes().get(key)

    @staticmethod
    def recursive_node_path(c, path: list[str], value: str or int or None, color_section: str = None):
        """ Creates or updates the node at the path. Intermediate nodes are always compound. """
        if len(path) == 0:
            return
        child = ContextWindowLogic.findByNodeKey(c, path[0])
        if child is None:
            child = CompoundMemoryChunk(c, path[0], roundColors(color_section)) if value is None or len(path) > 1 \
                else SingleMemoryChunk(c, path[0], value)
            c.getNodes()[path[0]] = child
            c.getInnerLayout().addWidget(child)
            ContextWindowLogic.recursive_node_path(child, path[1:], value, color_section)
        elif len(path) == 1:
            if isinstance(child, SingleMemoryChunk):
                child.setValue(value)
        else:
            ContextWindowLogic.recursive_node_path(child, path[1:], value, color_section)

    @staticmethod
    def removeNodeRecursive(c, path: list[str]):
        """ Removes the node at the path. The key is free again while the animation runs. """
        if len(path) == 0:
            return
        child = ContextWindowLogic.findByNodeKey(c, path[0])
        if child is not None:
            if len(path) == 1:
                del c.getNodes()[path[0]]
                child.rm()
            else:
                ContextWindowLogic.removeNodeRecursive(child, path[1:])

    def __init__(self, parent, name: str):
        super().__init__(parent, name)
        self._nodes: dict = {}

    def getNodes(self) -> dict:
        """ Returns the top-level nodes indexed by key. """
        return self._nodes

    def getInnerLayout(self) -> QVBoxLayout:
        """ Returns the layout that contains the top-level nodes. """
        return self._inner_layout

    def addNewNode(self, node_path: str, node_value: str or int or None = None):
        """ Creates or updates the node at a dotted path. """
        _path_members = node_path.split(".")
        ContextWindowLogic.recursive_node_path(self, _path_members, node_value, _path_members[0])

    def clearNodes(self):
        """ Deletes all nodes without animation. """
        self._nodes.clear()
        current_layout: QVBoxLayout = self.getInnerLayout()
        while current_layout.count() > 0:
            item = current_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()

    def removeNode(self, node_path: str):
        """ Removes the node at a dotted path with the removal animation. """
        ContextWindowLogic.removeNodeRecursive(self, node_path.split("."))

    def popLastNode(self, container=None) -> bool:
        """ Removes the deepest last node. Returns False if the container is empty. """
        container = self if container is None else container
        nodes = container.getNodes()
        if not nodes:
            return False
        key = next(reversed(nodes))
        widget = nodes[key]
        if isinstance(widget, SingleMemoryChunk) or not self.popLastNode(widget):
            del nodes[key]
            widget.hide()
            widget.deleteLater()
        return True


class ContextWindow(ContextWindowLogic):
    def __init__(self, parent, name: str):
        super().__init__(parent, name)
