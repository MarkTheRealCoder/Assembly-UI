from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import *

from Main.Graphics.Components.Codebox import Editor, Input, Output
from Main.Graphics.Components.Memory import Memory, MemoryOptions
from Main.Graphics.Components.Toolbar import ToolBar
from Main.Tools.Tools import find_path as getSS

BAHNSCHRIFT_12 = ("Bahnschrift", 12)

BLINK_BACKGROUND = "#787776"
# INSTRUCTION AND GUI OPTIONS BACKGROUND
IGO_BACKGROUND = "#1E1E1E"
CODE_DEF_FOREGROUND = "dark gray"
# INSTRUCTION AND GUI OPTIONS FOREGROUND
IGO_FOREGROUND = "#E48300"
SUBROUTINES_FOREGROUND = "#C1A402"
VALUES_FOREGROUND = "#0EA0A9"
# CURRENT LINE BACKGROUND
CL_BACKGROUND = "#191919"
# DEFAULT BACKGROUND
DEFAULT_BACKGROUND = '#171717'


class Window(QMainWindow):
    application: QApplication = None

    def __init__(self, app: QApplication):
        super(QMainWindow, self).__init__(None)
        Window.application = app

        self.lastState = Qt.WindowActive

        self.defineWindow()

        mwt: QWidget = QWidget(self)
        mwt.setObjectName("MainWidget")
        layout = QGridLayout(mwt)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.add_tool_bar(mwt), 0, 0, Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.add_first_column(mwt), 1, 0, Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(self.add_second_column(mwt), 1, 1, Qt.AlignLeft)
        self.setCentralWidget(mwt)
        with open(getSS("style.qss"), "r") as f:
            self.setStyleSheet(f.read())
        self.installEventFilter(self)

    def centerOnScreen(self):
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(x, y)

    def defineWindow(self):
        self.setWindowTitle("Assembly Stdio")
        self.setFixedSize(1200, 650)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.centerOnScreen()

    @staticmethod
    def add_tool_bar(mwt: QWidget):
        return ToolBar(mwt, Window.application.clipboard())

    @staticmethod
    def add_first_column(mwt: QWidget):
        widget: QWidget = QWidget(mwt)
        second_widget: QWidget = QWidget(widget)

        layout: QVBoxLayout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        second_layout: QHBoxLayout = QHBoxLayout(second_widget)
        second_layout.setSpacing(0)
        second_layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(Editor(mwt), 0, Qt.AlignTop | Qt.AlignLeft)
        second_layout.addWidget(Input(mwt), 0, Qt.AlignLeft)
        second_layout.addWidget(Output(mwt), 0, Qt.AlignLeft)
        second_widget.setLayout(second_layout)
        layout.addWidget(second_widget, 0, Qt.AlignTop | Qt.AlignLeft)
        widget.setLayout(layout)
        return widget

    @staticmethod
    def add_second_column(mwt: QWidget):
        widget: QWidget = QWidget(mwt)

        layout: QVBoxLayout = QVBoxLayout(widget)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)

        layout.addWidget(Memory(mwt), 0, Qt.AlignTop | Qt.AlignLeft)
        layout.addWidget(MemoryOptions(mwt), 0, Qt.AlignTop | Qt.AlignLeft)
        widget.setLayout(layout)
        return widget
"""
Creare una nuova struttura di layout con diverse tipologie incastrate tra loro.
"""








