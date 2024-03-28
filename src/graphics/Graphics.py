from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import *

from src.events.ResizeEvent import ResizeEvent
from src.graphics.components.Memory import Memory, MemoryOptions
from src.graphics.components.Toolbar import ToolBar
from src.graphics.components.editorcomponents.EditorWrapper import TabEditorWrapper
from src.graphics.components.editorcomponents.Input import Input
from src.graphics.components.editorcomponents.Output import Output
from src.tools.Tools import find_path as getSS, translateQSS, find_path, createLayout

INTEGER_MAX = 2147483647


class Window(QMainWindow):
    application: QApplication = None

    def __init__(self, app: QApplication):
        super(QMainWindow, self).__init__(None)
        QFontDatabase.addApplicationFont(find_path("AnonymousPro-Regular.ttf"))
        self.defineWindowSize()
        self.setWindowTitle("Assembly Stdio")
        Window.application = app

        self.lastState = Qt.WindowActive

        mwt: QWidget = QWidget(self)
        mwt.setObjectName("MainWidget")
        mwt.resize(self.size())
        self.setCentralWidget(mwt)
        self.setMainLayout(mwt)
        mwt.update()

        with open(getSS("style.qss"), "r") as f:
            self.setStyleSheet(translateQSS(f.read()))

        self.resizeEventHandler = ResizeEvent(self)

    def defineWindowSize(self):
        size: QSize = QDesktopWidget().screenGeometry()
        self.setMinimumSize(size.width() // 4 * 3, size.height() // 4 * 3)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.centerOnScreen()

    def centerOnScreen(self):
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def setMainLayout(self, mwt: QWidget):
        layout: QVBoxLayout = createLayout(QVBoxLayout, mwt)
        layout.addWidget(ToolBar(mwt, Window.application.clipboard()), 0)
        self.buildCoreComponents(mwt, layout)
        mwt.setLayout(layout)

    def buildCoreComponents(self, mwt: QWidget, layout: QVBoxLayout):

        layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        code_and_memory: QHBoxLayout = createLayout(QHBoxLayout, mwt) # Code and Memory
        IO_and_options: QHBoxLayout = createLayout(QHBoxLayout, mwt) # Secondary

        # Add to main layout
        layout.addLayout(code_and_memory)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Expanding, QSizePolicy.Fixed)) # Horizontal
        layout.addLayout(IO_and_options)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Expanding, QSizePolicy.Fixed)) # Horizontal

        layout.setStretchFactor(code_and_memory, 4)
        layout.setStretchFactor(IO_and_options, 1)

        # Add code and memory to their H layout
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)) # Vertical
        code_and_memory.addWidget(self.setSplitter(mwt), 1)
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)) # Vertical

        # Add input, output and memory options to their layout
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)) # Vertical
        IO_and_options.addWidget(Input(mwt), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)) # Vertical
        IO_and_options.addWidget(Output(mwt), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)) # Vertical
        IO_and_options.addWidget(MemoryOptions(mwt), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding)) # Vertical
        return layout

    def setSplitter(self, mwt: QWidget):
        cmResizer: QSplitter = QSplitter(mwt)
        cmResizer.setOrientation(Qt.Horizontal)
        cmResizer.setObjectName("Mem-CodeSplitter")
        cmResizer.setHandleWidth(7)
        cmResizer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        cmResizer.addWidget(TabEditorWrapper(mwt))
        cmResizer.addWidget(Memory(mwt, Window.application.clipboard()))
        cmResizer.setSizes([INTEGER_MAX, INTEGER_MAX])
        cmResizer.setStretchFactor(0, 1)
        cmResizer.setStretchFactor(1, 1)
        return cmResizer