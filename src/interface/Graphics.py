from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFontDatabase
from PyQt5.QtWidgets import *

from src.eventhandlers.Register import EventRegister
from src.eventhandlers.resize.Resizer import Resizer
from src.events.data.ClosingEvent import ClosingEvent
from src.events.data.ReadyEvent import ReadyEvent
from src.filesystem.DataManager import HandleJson
from src.filesystem.Folder import find_path
from src.interface.commons.Commons import createLayout
from src.interface.components.codespace.editorwrapper.EditorWrapper import EditorWrapper
from src.interface.components.codespace.io.Input import Input
from src.interface.components.codespace.io.Output import Output
from src.interface.components.memviewer.Memory import Memory, MemoryOptions
from src.interface.components.toolbar.Toolbar import ToolBar
from src.platform.Adaptability import translateQSS, Desktop
from src.signals.Variables import DataBase

INTEGER_MAX = 2147483647


@EventRegister.register(ClosingEvent, priority=EventRegister.LOW)
class Window(QMainWindow):
    application: QApplication = None

    def __init__(self, app: QApplication):
        super(QMainWindow, self).__init__(None)
        self.add_fonts()
        self.defineWindowSize()
        self.setWindowTitle("Assembly Stdio")
        Window.application = app

        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

        mwt: QWidget = QWidget(self)
        mwt.setObjectName("MainWidget")
        mwt.resize(self.size())
        self.setCentralWidget(mwt)
        self.setMainLayout(mwt)
        mwt.update()

        with open(find_path("style.qss"), "r") as f:
            app.setStyleSheet(translateQSS(f.read()))

        self.resizeEventHandler = Resizer(self, "Main")

    def onClosingEvent(self, event):
        self.close()

    def showEvent(self, event):
        hj = HandleJson.get_instance()
        hj.get_cwd()
        hj.get_font()
        super().showEvent(event)
        EventRegister.send(ReadyEvent(), arg="Main")

    def defineWindowSize(self):
        self.setMinimumSize(Desktop.sizeHint(3 / 4, 3 / 4))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.centerOnScreen()

    def centerOnScreen(self):
        screen_geometry = Desktop.getDesktopSize()
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

        code_and_memory: QHBoxLayout = createLayout(QHBoxLayout, mwt)   # Code and Memory
        IO_and_options: QHBoxLayout = createLayout(QHBoxLayout, mwt)    # Secondary

        # Add to main layout
        layout.addLayout(code_and_memory)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Expanding, QSizePolicy.Fixed))   # Horizontal
        layout.addLayout(IO_and_options)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Expanding, QSizePolicy.Fixed))   # Horizontal

        layout.setStretchFactor(code_and_memory, 4)
        layout.setStretchFactor(IO_and_options, 1)

        # Add code and memory to their H layout
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))  # Vertical
        code_and_memory.addWidget(self.setSplitter(mwt), 1)
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))  # Vertical

        # Add input, output and memory options to their layout
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        IO_and_options.addWidget(Input(mwt), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        IO_and_options.addWidget(Output(mwt), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        IO_and_options.addWidget(MemoryOptions(mwt), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        return layout

    def setSplitter(self, mwt: QWidget):
        cmResizer: QSplitter = QSplitter(mwt)
        cmResizer.splitterMoved.connect(lambda: DataBase.ON_SPLITTER_MOVE.setValue(True))
        cmResizer.setOrientation(Qt.Horizontal)
        cmResizer.setObjectName("Mem-CodeSplitter")
        cmResizer.setHandleWidth(7)
        cmResizer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        cmResizer.addWidget(EditorWrapper(mwt))
        cmResizer.addWidget(Memory(mwt, Window.application.clipboard()))
        cmResizer.setSizes([INTEGER_MAX, INTEGER_MAX])
        cmResizer.setStretchFactor(0, 1)
        cmResizer.setStretchFactor(1, 1)
        return cmResizer

    def add_fonts(self):
        QFontDatabase.addApplicationFont(find_path("AnonymousPro.ttf"))
        QFontDatabase.addApplicationFont(find_path("FiraCode.ttf"))
        QFontDatabase.addApplicationFont(find_path("Inconsolata.ttf"))
        QFontDatabase.addApplicationFont(find_path("Bahnschrift.ttf"))
        QFontDatabase.addApplicationFont(find_path("Monaco.ttf"))
        QFontDatabase.addApplicationFont(find_path("Fixedsys.ttf"))
        QFontDatabase.addApplicationFont(find_path("OCR-A.ttf"))

