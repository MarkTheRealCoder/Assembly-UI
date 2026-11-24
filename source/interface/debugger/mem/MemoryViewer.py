from PyQt5 import sip
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from source.interface.debugger.mem.ContextContainer import ContextContainer
from source.interface.debugger.mem.ContextWindow import ContextWindow
from source.interface.debugger.mem.MemoryHeader import MemoryHeader
from source.interface.debugger.mem.chunks import SingleMemoryChunk
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
    # Delay that lets the layouts place a new node before the viewer scrolls to it.
    ___FOLLOW_DELAY_MS = 30
    ___FOLLOW_MARGIN = 12

    def __init__(self, parent):
        super().__init__(parent)
        self.___follow_new_nodes: bool = False

    def addNewContext(self, name: str):
        """ Add a new context to the memory viewer """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        w.addContext(name)

    def addNodeToContext(self, context_name: str, node_path: str, value: str or int or list[int] or None = None,
                         order: int = None):
        """ Add a new Node into a specific context following the path provided.
            The above-mentioned path must follow the following grammar: id.id1.(...).node_name
            This path will create recursively the nodes: id which contains id1 which contains the other nodes
            that will ultimately contain node_name.
            Example: id -> id1 -> ... -> node_name: value
            The order is the position of the node among its siblings; None appends it.
            Returns the outermost node that the call created, or None.
        """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        context_window: ContextWindow = w.findContext(context_name)
        if context_window is not None:
            return context_window.addNewNode(node_path, value, order)
        return None

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

    def loadContexts(self, names: list[str], language: str, debug: bool = False):
        """
        Replace the contexts with the ones of a new program.
        In debug mode the viewer scrolls to each node that the program adds.
        """
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        w.reset()
        for name in names:
            w.addContext(name)
        self.mem_header.updateLanguage(language)
        self.mem_header.setWaiting(False)
        self.___follow_new_nodes = debug

    def setHexadecimal(self, hexadecimal: bool):
        """ Show every memory value in hexadecimal or in decimal """
        SingleMemoryChunk.setHexadecimal(hexadecimal)
        w: ContextContainer = self.mem_wrapper.exposeWidget()
        for chunk in w.findChildren(SingleMemoryChunk):
            chunk.refresh()

    def setWaitingInput(self, waiting: bool):
        """ Show or hide the animation that tells the user to type an input """
        self.mem_header.setWaiting(waiting)

    def stopFollowing(self):
        """ Stop scrolling to new nodes, for example at the end of the program """
        self.___follow_new_nodes = False

    def ___scrollTo(self, widget):
        if widget is None or sip.isdeleted(widget) or not widget.isVisible():
            return
        self.mem_wrapper.ensureWidgetVisible(widget, self.___FOLLOW_MARGIN, self.___FOLLOW_MARGIN)

    def applyUpdate(self, update):
        """ Apply an interpreter update as one repaint. """
        if not update.changed and not update.removed and update.instruction is None:
            return
        created = None
        self.setUpdatesEnabled(False)
        try:
            for context, path in update.removed:
                self.removeNodeFromContext(context, path)
            for context, path, value, order in update.changed:
                node = self.addNodeToContext(context, path, value, order)
                if node is not None:
                    created = node
            if update.instruction is not None:
                self.mem_header.updateInstruction(update.instruction, update.line)
                self.mem_header.updateScope(update.scope)
                self.mem_header.updateProgramCounter(max(update.pc, 0))
        finally:
            self.setUpdatesEnabled(True)

        if created is not None and self.___follow_new_nodes:
            QTimer.singleShot(self.___FOLLOW_DELAY_MS, lambda: self.___scrollTo(created))


class MemoryViewer(MemoryViewerLogic):
    def __init__(self, parent):
        super().__init__(parent)
