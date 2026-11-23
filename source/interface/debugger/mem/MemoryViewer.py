from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from source.interface.debugger.mem.ContextContainer import ContextContainer
from source.interface.debugger.mem.ContextWindow import ContextWindow
from source.interface.debugger.mem.MemoryHeader import MemoryHeader
from source.interface.shared import createLayout
from source.interface.templates import ScrollWrapper


class MemoryViewerGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MemoryViewer")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.mem_header = MemoryHeader(self)
        self.mem_wrapper = ScrollWrapper(self, ContextContainer, vscrollbar_policy="as_needed")

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.addWidget(self.mem_header, 0)
        layout.addWidget(self.mem_wrapper, 1)
        self.setLayout(layout)


class MemoryViewerLogic(MemoryViewerGraphics):
    def __init__(self, parent):
        super().__init__(parent)

    def addNewContext(self, name: str):
        """ Add a new context to the memory viewer """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        w.addContext(name)

    def addNodeToContext(self, context_name: str, node_path: str, value: str or int or list[int] or None = None):
        """ Add a new Node into a specific context following the path provided.
            The above-mentioned path must follow the following grammar: id.id1.(...).node_name
            This path will create recursively the nodes: id which contains id1 which contains the other nodes
            that will ultimately contain node_name.
            Example: id -> id1 -> ... -> node_name: value
        """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        context_window: ContextWindow = w.findContext(context_name)
        if context_window is not None:
            context_window.addNewNode(node_path, value)

    def removeNodeFromContext(self, context_name: str, node_path: str):
        """ Remove a node from a specific context following the path provided.
            The above-mentioned path must follow the following grammar: id.id1.(...).node_name
            This path will remove the node_name from the context if it exists.
        """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        context_window: ContextWindow = w.findContext(context_name)
        if context_window is not None:
            context_window.removeNode(node_path)

    def popLastFromContext(self, context_name: str):
        """ Remove the last node from a specific context. """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        context_window: ContextWindow = w.findContext(context_name)
        if context_window is not None:
            context_window.popLastNode()

    def loadContexts(self, names: list[str], language: str):
        """ Replace the contexts with the ones of a new program. """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        w.reset()
        for name in names:
            w.addContext(name)
        self.mem_header.updateLanguage(language)

    def applyUpdate(self, update):
        """ Apply an interpreter update as one repaint. """
        if not update.changed and not update.removed and update.instruction is None:
            return
        self.setUpdatesEnabled(False)
        try:
            for context, path in update.removed:
                self.removeNodeFromContext(context, path)
            for context, path, value in update.changed:
                self.addNodeToContext(context, path, value)
            if update.instruction is not None:
                self.mem_header.updateInstruction(update.instruction)
                self.mem_header.updateScope(update.scope)
                self.mem_header.updateProgramCounter(max(update.pc, 0))
        finally:
            self.setUpdatesEnabled(True)


class MemoryViewer(MemoryViewerLogic):
    def __init__(self, parent):
        super().__init__(parent)
