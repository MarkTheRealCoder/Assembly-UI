from PyQt5.QtCore import QTimer
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
        # Additional UI setup can be done here
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
        # Implementation of memory viewer logic goes here

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


class MemoryViewer(MemoryViewerLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for MemoryViewer
        self.addNewContext("REGISTERS")
        self.addNewContext("STACK")
        self.addNewContext("MEMORY")
        self.addNewContext("FLAGS")
        self.addNodeToContext("REGISTERS", "AX", None)
        self.addNodeToContext("REGISTERS", "BX", None)
        self.addNodeToContext("REGISTERS", "CX", None)
        self.addNodeToContext("REGISTERS", "DX", None)
        self.addNodeToContext("REGISTERS", "AX.AH", 0)
        self.addNodeToContext("REGISTERS", "AX.AL", 0)
        self.addNodeToContext("REGISTERS", "BX.BH", 0)
        self.addNodeToContext("REGISTERS", "BX.BL", 0)
        self.addNodeToContext("REGISTERS", "CX.CH", 0)
        self.addNodeToContext("REGISTERS", "CX.CL", 0)
        self.addNodeToContext("REGISTERS", "DX.DH", 0)
        self.addNodeToContext("REGISTERS", "DX.DL", 0)
        self.addNodeToContext("REGISTERS", "DX.DL", 2)
        self.addNodeToContext("STACK", "0x00000000", 0)
        self.addNodeToContext("STACK", "0x00000004", 0)
        self.addNodeToContext("STACK", "0x00000008", 0)
        self.addNodeToContext("STACK", "0x0000000C", 0)
        self.addNodeToContext("STACK", "0x00000010", 0)
        self.addNodeToContext("STACK", "0x00000014", 0)
        self.addNodeToContext("STACK", "0x00000018", 0)
        self.addNodeToContext("STACK", "0x0000001C", 0)
        self.addNodeToContext("STACK", "0x00000020", 0)
        self.addNodeToContext("STACK", "0x00000024", 0)
        self.addNodeToContext("STACK", "0x00000028", 0)
        self.addNodeToContext("STACK", "function.function")
        self.addNodeToContext("STACK", "function.function.0x00000024", 12)
        self.addNodeToContext("STACK", "function.function.function.function.function.function")
        self.addNodeToContext("MEMORY", "0x00000000", 0)
        self.addNodeToContext("MEMORY", "0x00000004", 0)
        self.addNodeToContext("MEMORY", "0x00000008", 0)
        self.addNodeToContext("MEMORY", "0x0000000C", 0)
        self.addNodeToContext("MEMORY", "0x00000010", 0)
        self.addNodeToContext("MEMORY", "0x00000014", 0)
        self.addNodeToContext("MEMORY", "0x00000018", 0)
        self.addNodeToContext("MEMORY", "0x0000001C", 0)
        self.addNodeToContext("MEMORY", "0x00000020", 0)
        self.addNodeToContext("FLAGS", "ZF", 0)
        self.addNodeToContext("FLAGS", "SF", 0)
        self.addNodeToContext("FLAGS", "OF", 0)
        self.addNodeToContext("FLAGS", "CF", 0)
        self.addNodeToContext("FLAGS", "AF", 0)

        QTimer.singleShot(10000, lambda: self.removeNodeFromContext("STACK", "function.function.function.function.function.function"))
        QTimer.singleShot(11000, lambda: self.removeNodeFromContext("STACK", "function.function.function.function.function"))
        QTimer.singleShot(12000, lambda: self.removeNodeFromContext("STACK", "function.function.function.function"))
        QTimer.singleShot(13000, lambda: self.removeNodeFromContext("STACK", "function.function.function"))
        QTimer.singleShot(14000, lambda: self.removeNodeFromContext("STACK", "function.function"))
        QTimer.singleShot(15000, lambda: self.removeNodeFromContext("STACK", "function"))


