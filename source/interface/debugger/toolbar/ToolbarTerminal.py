from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QSpacerItem

from source.interface.debugger import ExecutionContext
from source.interface.debugger.toolbar.ClearButton import ClearButton
from source.interface.debugger.toolbar.FindButton import FindButton
from source.interface.debugger.toolbar.ScrollButton import ScrollButton
from source.interface.shared import createLayout


class ToolbarGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ToolbarTerminal")
        # Additional UI setup can be done here
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(44)

        self._find_button: FindButton = FindButton(self)

        self._scroll_up_button: ScrollButton = ScrollButton(self, "up")
        self._scroll_down_button: ScrollButton = ScrollButton(self, "down")
        self._clear_button: ClearButton = ClearButton(self)

        self.addButtons()

    def addButtons(self):
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.setSpacing(10)
        layout.addWidget(self._scroll_up_button)
        layout.addWidget(self._scroll_down_button)
        layout.addWidget(self._clear_button)
        layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Minimum))
        layout.addWidget(self._find_button)
        layout.addSpacerItem(QSpacerItem(80, 20, QSizePolicy.MinimumExpanding, QSizePolicy.Minimum))
        self.setLayout(layout)


class ToolbarLogic(ToolbarGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of toolbar logic goes here
        self.exec_context: ExecutionContext = parent

    def clearTerminal(self):
        if self._clear_button.property("active"):
            self.exec_context.clearTerminal()
            self._clear_button.inactiveProtocol()
        else:
            self._clear_button.activeProtocol()

    def scrollDownTerminal(self):
        self.exec_context.scrollDownTerminal()

    def scrollUpTerminal(self):
        self.exec_context.scrollUpTerminal()

    def findTerminal(self):
        self.exec_context.findTerminal()


class Toolbar(ToolbarLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for Toolbar
        # todo : implement toolbar comms to debugger and terminal
        self._find_button.clicked.connect(self.findTerminal)

        self._clear_button.clicked.connect(self.clearTerminal)
        self._scroll_down_button.clicked.connect(self.scrollDownTerminal)
        self._scroll_up_button.clicked.connect(self.scrollUpTerminal)





