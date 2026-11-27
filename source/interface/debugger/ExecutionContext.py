from PyQt5.QtWidgets import QFrame, QSizePolicy, QHBoxLayout, QVBoxLayout, QTextEdit

from source.comms import Database
from source.comms.events import ClosingEvent, RunEvent
from source.comms.handlers import EventRegister
from source.filesystem.documents import Document
from source.interface import createLayout, Settings, Splitter
from source.interface.debugger.mem import MemoryViewer
from source.interface.debugger.term import Terminal
from source.interface.debugger.toolbar import ToolbarExecution, ToolbarTerminal
from source.interface.templates import FindWidget
from source.interpreter import Interpreter, InterpreterUpdate, InterpreterWorker, parseDiagnostics


TERMINAL_MIN_WIDTH = 140
MEMORY_MIN_WIDTH = 200
TOOLBAR_SEPARATOR_WIDTH = 1


class ExecutionContextGraphics(QFrame):
    def __init__(self, mwt):
        super().__init__(mwt)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName("ExecutionContext")

        self.terminal: Terminal = Terminal(self)
        self.memory_viewer: MemoryViewer = MemoryViewer(self)
        self.toolbar_t: ToolbarTerminal = ToolbarTerminal(self)
        self.toolbar_e: ToolbarExecution = ToolbarExecution(self)

        # The toolbars span the whole width with fixed 2:3 proportions: the splitter below moves only the
        # terminal and the memory viewer.
        toolbars_frame = QFrame(self)
        toolbars_frame.setObjectName("ExecutionToolbars")
        toolbars: QHBoxLayout = createLayout(QHBoxLayout, toolbars_frame)
        toolbars.setSpacing(TOOLBAR_SEPARATOR_WIDTH)
        for toolbar, stretch in ((self.toolbar_t, 2), (self.toolbar_e, 3)):
            policy = toolbar.sizePolicy()
            policy.setHorizontalPolicy(QSizePolicy.Ignored)
            toolbar.setSizePolicy(policy)
            toolbars.addWidget(toolbar, stretch)

        terminal_pane = QFrame(self)
        terminal_pane.setObjectName("TerminalPane")
        vlayout: QVBoxLayout = createLayout(QVBoxLayout, terminal_pane)
        vlayout.addWidget(FindWidget(self,  "terminal"), 1)
        vlayout.addWidget(self.terminal, 3)

        memory_pane = QFrame(self)
        memory_pane.setObjectName("MemoryPane")
        vlayout2: QVBoxLayout = createLayout(QVBoxLayout, memory_pane)
        vlayout2.addWidget(self.memory_viewer, 1)

        self.splitter: Splitter = Splitter(self, "Term-MemSplitter", "layout/terminal-memory-splitter")
        self.splitter.addPane(terminal_pane, TERMINAL_MIN_WIDTH, 2)
        self.splitter.addPane(memory_pane, MEMORY_MIN_WIDTH, 3)
        self.splitter.restoreSizes([2, 3])

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.addWidget(toolbars_frame)
        layout.addWidget(self.splitter, 1)
        self.setLayout(layout)
        Database.ON_SPLITTER_DRAG.connect(self.___freezeTerminalWrap)

    def ___freezeTerminalWrap(self):
        """
        Keep the terminal text wrapped at its width while a splitter handle is dragged.
        Rewrapping the whole output at every pixel is what makes the drag lag; it happens once on release instead.
        """
        if Database.ON_SPLITTER_DRAG.getValue():
            self.terminal.setLineWrapColumnOrWidth(self.terminal.viewport().width())
            self.terminal.setLineWrapMode(QTextEdit.FixedPixelWidth)
        else:
            self.terminal.setLineWrapMode(QTextEdit.WidgetWidth)

    def splitterMinimumWidth(self) -> int:
        """ Narrowest width at which the terminal and the memory viewer keep their own minimum """
        return TERMINAL_MIN_WIDTH + MEMORY_MIN_WIDTH + self.splitter.handleWidth()


class ExecutionContextLogic(ExecutionContextGraphics):
    """ Connects the toolbar, the terminal and the memory viewer to the interpreter. """

    ___MAX_RUN_OUTPUT = 200_000
    ___WORKER_WAIT_MS = 1000

    def __init__(self, mwt):
        super().__init__(mwt)
        self.___handle: Interpreter = None
        self.___worker: InterpreterWorker = None
        self.___output_size: int = 0
        self.___path: str = None
        self.___diagnostics: list = []

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
            self.terminal.prompt()
            return False

        EventRegister.send(RunEvent(), "Editor")
        self.___diagnostics = []
        Database.ON_DIAGNOSTICS.setValue((path, []))
        try:
            document = Document(path)
            handle = Interpreter.get_handle(hash(path), document)
            contexts = handle.contexts
        except Exception as error:
            self.terminal.error(f"Could not start the interpreter: {error}")
            self.terminal.prompt()
            return False

        self.___handle = handle
        self.___output_size = 0
        self.___path = path
        self.memory_viewer.loadContexts(contexts, handle.language, debug)
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
        """
        Send the characters of the lines typed in the terminal to the program, without newlines.
        A line with a character code above the limit of the program is not sent.
        """
        if self.___handle is None:
            return
        limit = self.___handle.max_input_value
        for line in lines:
            invalid = next((c for c in line if ord(c) > limit), None)
            if invalid is not None:
                self.terminal.warning(f"Input not sent: '{invalid}' has code {ord(invalid)}. "
                                      f"The program reads one byte per character, from 0 to {limit}.")
                continue
            if self.___handle.feed(line):
                self.memory_viewer.setWaitingInput(False)
            else:
                self.terminal.warning("Input not sent: the program does not accept more input.")

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
            self.___reportDiagnostics(update.warnings)
        if update.output:
            self.___writeOutput(update.output)
        self.memory_viewer.applyUpdate(update)
        self.memory_viewer.setWaitingInput(update.state == "WAITING_INPUT")
        if update.line > 0 and not update.terminal:
            Database.ON_EXECUTION_LINE.setValue((self.___path, update.line))

        if update.terminal:
            self.___finishExecution(update)
        elif worker is not None:
            worker.acknowledge()

    def ___reportDiagnostics(self, text: str):
        """ Show in the editor the positioned errors and warnings found in a message of the program """
        found = parseDiagnostics(text)
        if found and self.___path:
            self.___diagnostics.extend(found)
            Database.ON_DIAGNOSTICS.setValue((self.___path, list(self.___diagnostics)))

    def ___finishExecution(self, update: InterpreterUpdate):
        """ Report the result of the program, print the prompt again and restore the controls """
        self.terminal.endProgram()
        if update.state == "FAILED":
            self.terminal.error(update.message or "Execution failed.")
            self.___reportDiagnostics(update.message)
        elif update.state == "STOPPED":
            self.terminal.warning("Execution stopped.")
        else:
            self.terminal.info(f"Execution finished with code {update.exit_code}.")
        self.terminal.prompt()
        self.memory_viewer.setWaitingInput(False)
        self.memory_viewer.stopFollowing()
        Database.ON_EXECUTION_LINE.setValue((self.___path, -1))
        self.___handle = None
        self.___worker = None
        self.___path = None
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
