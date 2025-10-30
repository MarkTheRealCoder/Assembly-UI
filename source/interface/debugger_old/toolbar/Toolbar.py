from PyQt5.QtWidgets import QWidget, QFrame, QGridLayout

from source.interface.shared import createLayout
from .Button import DebuggerButton


class DebuggerToolbar(QFrame):
    def __init__(self, mwt: QWidget):
        super(QFrame, self).__init__(parent=mwt)
        self.setObjectName("DebuggerToolbar")

    def setupUI(self):
        self.setFrameShape(QFrame.StyledPanel)
        self.setFrameShadow(QFrame.Raised)
        layout: QGridLayout = createLayout(QGridLayout, self)

        run = DebuggerButton(self)
        debug = DebuggerButton(self)
        stop = DebuggerButton(self)

        layout.addWidget()

        step_ahead = DebuggerButton(self)
        step_ahead10 = DebuggerButton(self)

