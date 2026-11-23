from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QVBoxLayout, QSpacerItem

from source.comms.events import ClosingEvent, RunEvent
from source.comms.handlers import EventRegister
from source.filesystem.documents import Document
from source.interface.debugger.mem import MemoryViewer
from source.interface.debugger.term import Terminal
from source.interface.debugger.toolbar import ToolbarExecution
from source.interface.debugger.toolbar import ToolbarTerminal
from source.interface.shared import createLayout, Settings
from source.interface.templates import FindWidget
from source.interpreter import Interpreter, InterpreterUpdate, InterpreterWorker


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

        vlayout: QVBoxLayout = createLayout(QVBoxLayout)
        vlayout.addWidget(self.toolbar_t)
        vlayout.addWidget(FindWidget(self,  "terminal"), 1)
        vlayout.addWidget(self.terminal, 3)

        vlayout2: QVBoxLayout = createLayout(QVBoxLayout)
        vlayout2.addWidget(self.toolbar_e)
        vlayout2.addWidget(self.memory_viewer, 1)

        layout.addLayout(vlayout, 2)
        layout.addSpacerItem(QSpacerItem(1, 1, QSizePolicy.Minimum, QSizePolicy.Expanding))
        layout.addLayout(vlayout2, 3)

        self.setLayout(layout)


class ExecutionContextLogic(ExecutionContextGraphics):
    """ Connects the toolbar, the terminal and the memory viewer to the interpreter. """

    ___MAX_RUN_OUTPUT = 200_000
    ___WORKER_WAIT_MS = 1000

    def __init__(self, mwt):
        super().__init__(mwt)
        self.___handle: Interpreter = None
        self.___worker: InterpreterWorker = None
        self.___output_size: int = 0

    def clearTerminal(self):
        self.terminal.clear()

    def scrollDownTerminal(self):
        self.terminal.scrollDown()

    def scrollUpTerminal(self):
        self.terminal.scrollUp()

    def findTerminal(self):
        self.terminal.openFindWidget()

    def startExecution(self, debug: bool = False) -> bool:
        """ Save and start the current document. Return True if the program started. """
        if self.___handle is not None:
            return False

        path = Settings.get("editor/current", None)
        if not path:
            self.terminal.error("No file is open.")
            return False

        EventRegister.send(RunEvent(debug), "Editor")
        try:
            document = Document(path)
            handle = Interpreter.get_handle(hash(path), document)
            contexts = handle.contexts
        except Exception as error:
            self.terminal.error(f"Could not start the interpreter: {error}")
            return False

        self.___handle = handle
        self.___output_size = 0
        self.memory_viewer.loadContexts(contexts, handle.language)
        self.terminal.beginProgram(self.feedInput)

        self.___worker = InterpreterWorker(self, handle)
        self.___worker.updated.connect(self.___applyUpdate)
        self.___worker.finished.connect(self.___worker.deleteLater)
        handle.interpret(debug)
        self.___worker.start()
        return True

    def stopExecution(self):
        """ Request the end of the running program """
        if self.___handle is not None:
            self.___handle.terminate()

    def stepExecution(self, count: int = 1):
        """ Execute a number of instructions of the paused program """
        if self.___handle is not None:
            self.___handle.step(count)

    def feedInput(self, lines: list[str]):
        """ Send the lines typed in the terminal to the program """
        if self.___handle is not None:
            for line in lines:
                self.___handle.feed(line)

    def ___writeOutput(self, text: str):
        """ Write program output up to the limit of one run """
        remaining = self.___MAX_RUN_OUTPUT - self.___output_size
        if remaining > 0:
            self.terminal.writeProgram(text[:remaining])
            if len(text) >= remaining:
                self.terminal.writeProgram("\n[Output limit reached: the terminal hides the remaining output.]\n")
        self.___output_size += len(text)

    def ___applyUpdate(self, update: InterpreterUpdate):
        """ Apply an update of the program on the GUI thread """
        worker = self.___worker
        if update.warnings:
            self.terminal.warning(update.warnings)
        if update.output:
            self.___writeOutput(update.output)
        self.memory_viewer.applyUpdate(update)

        if update.terminal:
            self.___finishExecution(update)
        elif worker is not None:
            worker.acknowledge()

    def ___finishExecution(self, update: InterpreterUpdate):
        """ Report the result of the program and restore the controls """
        self.terminal.endProgram()
        if update.state == "FAILED":
            self.terminal.error(update.message or "Execution failed.")
        elif update.state == "STOPPED":
            self.terminal.warning("Execution stopped.")
        else:
            self.terminal.info(f"Execution finished with code {update.exit_code}.")
        self.___handle = None
        self.___worker = None
        self.toolbar_e.executionEnded()

    def shutdownExecution(self):
        """ Stop the program and its worker before the application exits """
        worker = self.___worker
        if self.___handle is not None:
            self.___handle.terminate()
        if worker is not None:
            worker.requestInterruption()
            worker.wait(self.___WORKER_WAIT_MS)
        self.___handle = None
        self.___worker = None


@EventRegister.register(ClosingEvent, priority=EventRegister.HIGH)
class ExecutionContext(ExecutionContextLogic):
    def __init__(self, mwt):
        super().__init__(mwt)

    def onClosingEvent(self, e: ClosingEvent):
        self.shutdownExecution()
        e.accept()
