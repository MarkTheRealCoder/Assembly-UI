from typing import TYPE_CHECKING

from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QSpacerItem

from source.interface import createLayout
from source.interface.debugger.toolbar.ClearButton import ClearButton
from source.interface.debugger.toolbar.FindButton import FindButton
from source.interface.debugger.toolbar.ScrollButton import ScrollButton

if TYPE_CHECKING:
    # Only for the annotations: ExecutionContext imports this toolbar, so the package does not hold it yet.
    from source.interface.debugger import ExecutionContext


class ToolbarGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ToolbarTerminal")
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
        layout.addSpacerItem(QSpacerItem(0, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))
        self.setLayout(layout)


class ToolbarLogic(ToolbarGraphics):
    def __init__(self, parent):
        super().__init__(parent)
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
        self._find_button.clicked.connect(self.findTerminal)

        self._clear_button.clicked.connect(self.clearTerminal)
        self._scroll_down_button.clicked.connect(self.scrollDownTerminal)
        self._scroll_up_button.clicked.connect(self.scrollUpTerminal)


