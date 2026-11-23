import threading

import jpype
from PyQt5.QtCore import QThread, pyqtSignal

from source.interpreter.Interpreter import Interpreter, InterpreterUpdate


class InterpreterWorker(QThread):
    """
    Reads the updates of an interpreter outside the GUI thread.
    The worker waits for an acknowledgement after each update, so a slow GUI also slows the program.
    """
    updated = pyqtSignal(object)

    ___READ_TIMEOUT_MS = 200
    ___ACK_TIMEOUT_S = 0.2

    def __init__(self, parent, handle: Interpreter):
        super().__init__(parent)
        self.___handle = handle
        self.___ack = threading.Semaphore(0)

    def acknowledge(self):
        """ Allows the worker to read the next update. """
        self.___ack.release()

    def run(self):
        try:
            while not self.isInterruptionRequested():
                update = self.___handle.read(self.___READ_TIMEOUT_MS)
                if update is None:
                    continue
                self.updated.emit(update)
                if update.terminal:
                    return
                while not self.___ack.acquire(timeout=self.___ACK_TIMEOUT_S):
                    if self.isInterruptionRequested():
                        return
        except Exception as error:
            # PyQt aborts the application if an exception leaves QThread.run.
            self.___handle.terminate()
            self.updated.emit(InterpreterUpdate(
                "FAILED", True, 1, f"Interpreter connection failed: {error}", None, -1, None, None, "", [], []
            ))
        finally:
            if jpype.isJVMStarted():
                jpype.java.lang.Thread.detach()
