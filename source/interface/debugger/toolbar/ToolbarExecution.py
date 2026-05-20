from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QHBoxLayout, QSizePolicy, QFrame

from source.interface.debugger import ExecutionContext
from source.interface.debugger.toolbar.RunButton import RunButton
from source.interface.debugger.toolbar.StepButton import StepButton
from source.interface.debugger.toolbar.StopButton import StopButton
from source.interface.debugger.toolbar.TimedExecutionButton import TimedExecutionButton
from source.interface.debugger.toolbar.TimedExecutionTickPicker import TimedExecutionTickPicker
from source.interface.shared import createLayout


class ToolbarGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ToolbarExecution")
        # Additional UI setup can be done here
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setFrameShape(QFrame.StyledPanel)
        self.setFixedHeight(44)

        self._separator = QFrame(self)
        self._separator.setFrameShape(QFrame.Shape.VLine)
        self._separator.setFrameShadow(QFrame.Shadow.Sunken)
        self._separator.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self._separator.setFixedHeight(22)
        self._separator.setStyleSheet("background-color: #CCCCCC;")
        self._separator.setFixedWidth(1)
        self._separator.hide()

        self._run_button: RunButton = RunButton(self)
        self._debug_button: RunButton = RunButton(self, icon_path="debug.svg")
        self._stop_button: StopButton = StopButton(self)
        self._step_ahead_button: StepButton = StepButton(self, 1)
        self._step_ahead_10_button: StepButton = StepButton(self, 10)
        self._timedisplay_tick: TimedExecutionTickPicker = TimedExecutionTickPicker(self)
        self._start_timedisplay_button: TimedExecutionButton = TimedExecutionButton(self)

        self._timedisplay_tick.currentIndexChanged.connect(lambda: self._start_timedisplay_button.update_interval(self._timedisplay_tick.currentData()))

        self.addButtons()

    def addButtons(self):
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.setAlignment(Qt.AlignLeft)
        layout.setSpacing(4)
        layout.addWidget(self._run_button)
        layout.addWidget(self._debug_button)
        layout.addWidget(self._stop_button)
        layout.addSpacing(32)
        layout.addWidget(self._step_ahead_button)
        layout.addWidget(self._step_ahead_10_button)
        layout.addSpacing(4)
        layout.addWidget(self._separator)
        layout.addSpacing(4)
        layout.addWidget(self._timedisplay_tick, 1)
        layout.addWidget(self._start_timedisplay_button)
        self.setLayout(layout)

    def runGraphic(self, debug: bool = False):
        if debug:
            self._stop_button.enable()
            self._debug_button.activeProtocol()
            self._run_button.inactiveProtocol()
            self._run_button.disable()
            self._step_ahead_button.enable()
            self._step_ahead_10_button.enable()
            self._start_timedisplay_button.enable()
            self._timedisplay_tick.enable()
            self._separator.show()
        else:
            self._stop_button.enable()
            self._run_button.activeProtocol()
            self._debug_button.inactiveProtocol()
            self._debug_button.disable()

    def stopGraphic(self):
        self._stop_button.disable()
        self._run_button.enable()
        self._debug_button.enable()
        self._run_button.inactiveProtocol()
        self._debug_button.inactiveProtocol()
        self._step_ahead_button.disable()
        self._step_ahead_10_button.disable()
        self._start_timedisplay_button.disable()
        self._timedisplay_tick.disable()
        self._separator.hide()


class ToolbarLogic(ToolbarGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of toolbar logic goes here
        self.exec_context: ExecutionContext = parent

    def run(self, debug: bool = False):
        self.runGraphic(debug)
        #EventRegister.send(RunEvent(debug), "Graphic")

    def stop(self):
        self.stopGraphic()


class Toolbar(ToolbarLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for Toolbar
        # todo : implement toolbar comms to debugger and terminal

        self._run_button.clicked.connect(self.run)
        self._debug_button.clicked.connect(lambda: self.run(True))
        self._stop_button.clicked.connect(self.stop)