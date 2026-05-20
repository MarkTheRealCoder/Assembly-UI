from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QVBoxLayout, QSpacerItem

from source.interface.debugger.mem import MemoryViewer
from source.interface.debugger.term import Terminal
from source.interface.debugger.toolbar import ToolbarExecution
from source.interface.debugger.toolbar import ToolbarTerminal
from source.interface.shared import createLayout
from source.interface.templates import FindWidget


class ExecutionContextGraphics(QFrame):
    def __init__(self, mwt):
        super().__init__(mwt)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName("ExecutionContext")

        self.terminal: Terminal = Terminal(self)
        self.memory_viewer: MemoryViewer = MemoryViewer(self)
        self.toolbar_t: ToolbarTerminal = ToolbarTerminal(self)
        self.toolbar_e: ToolbarExecution = ToolbarExecution(self)

        layout: QHBoxLayout = createLayout(QHBoxLayout, self)

        # vlayout for terminal and its toolbar
        vlayout: QVBoxLayout = createLayout(QVBoxLayout, self)
        vlayout.addWidget(self.toolbar_t)
        vlayout.addWidget(FindWidget(self,  "terminal"), 1)
        vlayout.addWidget(self.terminal, 3)

        # vlayout for execution toolbar and its memory viewer
        vlayout2: QVBoxLayout = createLayout(QVBoxLayout, self)
        vlayout2.addWidget(self.toolbar_e)
        vlayout2.addWidget(self.memory_viewer, 1)


        layout.addLayout(vlayout, 2)
        layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(vlayout2, 3)

        self.setLayout(layout)


class ExecutionContextLogic(ExecutionContextGraphics):
    def __init__(self, mwt):
        super().__init__(mwt)
        # Implementation of execution context logic goes here

    def clearTerminal(self):
        self.terminal.clear()

    def scrollDownTerminal(self):
        self.terminal.scrollDown()

    def scrollUpTerminal(self):
        self.terminal.scrollUp()

    def findTerminal(self):
        self.terminal.openFindWidget()


class ExecutionContext(ExecutionContextLogic):
    def __init__(self, mwt):
        super().__init__(mwt)
        # Additional initialization for ExecutionContext
