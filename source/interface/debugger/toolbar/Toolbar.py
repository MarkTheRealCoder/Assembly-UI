from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QSpacerItem

from source.interface.debugger import ExecutionContext
from source.interface.debugger.toolbar.ClearButton import ClearButton
from source.interface.debugger.toolbar.FindButton import FindButton
from source.interface.debugger.toolbar.RunButton import RunButton
from source.interface.debugger.toolbar.ScrollButton import ScrollButton
from source.interface.debugger.toolbar.StopButton import StopButton
from source.interface.shared import createLayout


class ToolbarGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ExecutionToolbar")
        # Additional UI setup can be done here
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(44)

        self._placeholder: QSpacerItem = QSpacerItem(40, 30, QSizePolicy.Maximum, QSizePolicy.Maximum)

        self._find_button: FindButton = FindButton(self)

        self._scroll_up_button: ScrollButton = ScrollButton(self, "up")
        self._scroll_down_button: ScrollButton = ScrollButton(self, "down")
        self._clear_button: ClearButton = ClearButton(self)

        self._run_button: RunButton = RunButton(self)
        self._debug_button: RunButton = RunButton(self, icon_path="debug.svg")
        self._stop_button: StopButton = StopButton(self)

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
        layout.addWidget(self._run_button)
        layout.addWidget(self._debug_button)
        layout.addWidget(self._stop_button)
        layout.addSpacing(40)
        layout.addSpacerItem(self._placeholder)
        self.setLayout(layout)

    def runGraphic(self, debug: bool = False):
        if debug:
            self._stop_button.enable()
            self._debug_button.activeProtocol()
            self._run_button.inactiveProtocol()
            self._run_button.disable()
        else:
            self._stop_button.enable()
            self._run_button.activeProtocol()
            self._debug_button.inactiveProtocol()
            self._debug_button.disable()
        self.layout().removeItem(self._placeholder)

    def stopGraphic(self):
        self._stop_button.disable()
        self._run_button.enable()
        self._debug_button.enable()
        self._run_button.inactiveProtocol()
        self._debug_button.inactiveProtocol()
        self.layout().addSpacerItem(self._placeholder)


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

    def run(self, debug: bool = False):
        self.runGraphic(debug)
        #EventRegister.send(RunEvent(debug), "Graphic")

    def stop(self):
        self.stopGraphic()

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

        self._run_button.clicked.connect(self.run)
        self._debug_button.clicked.connect(lambda: self.run(True))
        self._stop_button.clicked.connect(self.stop)





