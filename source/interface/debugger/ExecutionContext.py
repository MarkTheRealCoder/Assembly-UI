from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QVBoxLayout

from source.interface.debugger.mem import MemoryViewer
from source.interface.debugger.term import Terminal
from source.interface.debugger.toolbar import Toolbar
from source.interface.shared import createLayout
from source.interface.templates import FindWidget

"""var(---generic-tab-color)"""

class ExecutionContextGraphics(QFrame):
    def __init__(self, mwt):
        super().__init__(mwt)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName("ExecutionContext")

        self.terminal: Terminal = Terminal(self)
        self.memory_viewer: MemoryViewer = MemoryViewer(self)
        self.toolbar: Toolbar = Toolbar(self)

        layout = createLayout(QVBoxLayout, self)

        hlayout: QHBoxLayout = createLayout(QHBoxLayout, self)

        vlayout: QVBoxLayout = createLayout(QVBoxLayout, self)

        vlayout.addWidget(FindWidget(self,  "terminal"), 1)
        vlayout.addWidget(self.terminal, 3)

        hlayout.addLayout(vlayout)
        hlayout.addWidget(self.memory_viewer)

        layout.addWidget(self.toolbar, 2)
        layout.addLayout(hlayout, 1)
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
