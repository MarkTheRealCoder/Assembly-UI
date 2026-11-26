from typing import TYPE_CHECKING

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QHBoxLayout, QSizePolicy, QFrame

from source.interface import createLayout
from source.interface.debugger.toolbar.MemoryInfoButton import MemoryInfoButton
from source.interface.debugger.toolbar.NumberBasePicker import NumberBasePicker
from source.interface.debugger.toolbar.RunButton import RunButton
from source.interface.debugger.toolbar.StepButton import StepButton
from source.interface.debugger.toolbar.StopButton import StopButton
from source.interface.debugger.toolbar.TimedExecutionButton import TimedExecutionButton
from source.interface.debugger.toolbar.TimedExecutionTickPicker import TimedExecutionTickPicker

if TYPE_CHECKING:
    # Only for the annotations: ExecutionContext imports this toolbar, so the package does not hold it yet.
    from source.interface.debugger import ExecutionContext


class ToolbarGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ToolbarExecution")
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
        self._number_base_picker: NumberBasePicker = NumberBasePicker(self)
        self._memory_info_button: MemoryInfoButton = MemoryInfoButton(self)

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
        layout.addStretch(1)
        layout.addWidget(self._memory_info_button)
        layout.addWidget(self._number_base_picker)
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
        self.exec_context: ExecutionContext = parent
        self._step_timer = QTimer(self)

    def run(self, debug: bool = False):
        """ Start the current program and update the buttons if it starts """
        if self.exec_context.startExecution(debug):
            self.runGraphic(debug)

    def stop(self):
        """ Request the end of the current program """
        self.exec_context.stopExecution()

    def step(self, count: int = 1):
        """ Execute a number of instructions of the paused program """
        self.exec_context.stepExecution(count)

    def toggleTimedExecution(self):
        """ Start or stop the automatic execution """
        if self._start_timedisplay_button.isActive():
            self._step_timer.start(self._timedisplay_tick.currentData())
        else:
            self._step_timer.stop()

    def updateTimedInterval(self):
        """ Apply the selected interval to the running automatic execution """
        if self._step_timer.isActive():
            self._step_timer.setInterval(self._timedisplay_tick.currentData())

    def changeNumberBase(self, base: int):
        """ Show the memory values in base 16, 10 or 8 """
        self.exec_context.memory_viewer.setNumberBase(base)

    def executionEnded(self):
        """ Restore the buttons after the end of the program """
        self._step_timer.stop()
        self.stopGraphic()


class Toolbar(ToolbarLogic):
    def __init__(self, parent):
        super().__init__(parent)

        self._run_button.clicked.connect(lambda: self.run(False))
        self._debug_button.clicked.connect(lambda: self.run(True))
        self._stop_button.clicked.connect(self.stop)
        self._step_ahead_button.stepRequested.connect(self.step)
        self._step_ahead_10_button.stepRequested.connect(self.step)
        self._start_timedisplay_button.clicked.connect(self.toggleTimedExecution)
        self._timedisplay_tick.currentIndexChanged.connect(self.updateTimedInterval)
        self._step_timer.timeout.connect(self.step)
        self._number_base_picker.baseChanged.connect(self.changeNumberBase)