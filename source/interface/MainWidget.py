from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSplitter, QSizePolicy, QVBoxLayout, QHBoxLayout, QSpacerItem

from source.comms.events import EditorResizeEvent
from source.comms.handlers import EventRegister
from source.interface.debugger.Memory import Memory
from source.interface.debugger.options import OptionsContainer
from source.interface.editor.EditorWrapper import EditorWrapper
from source.interface.io.Input import Input
from source.interface.io.Output import Output
from source.interface.shared import createLayout
from source.interface.titlebar import Toolbar

INTEGER_MAX = 2147483647


class MainWidgetGraphics(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(parent.size())
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setMainLayout()

    def setMainLayout(self):
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.addWidget(Toolbar(self), 0)
        self.buildCoreComponents(layout)
        self.setLayout(layout)

    def buildCoreComponents(self, layout: QVBoxLayout):

        layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        code_and_memory: QHBoxLayout = createLayout(QHBoxLayout, self)   # Code and Memory
        IO_and_options: QHBoxLayout = createLayout(QHBoxLayout, self)    # Secondary

        # Add to main layout
        layout.addLayout(code_and_memory)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Expanding, QSizePolicy.Fixed))   # Horizontal
        layout.addLayout(IO_and_options)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Expanding, QSizePolicy.Fixed))   # Horizontal

        layout.setStretchFactor(code_and_memory, 4)
        layout.setStretchFactor(IO_and_options, 1)

        # Add code and memory to their H layout
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))  # Vertical
        code_and_memory.addWidget(self.setSplitter(), 1)
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))  # Vertical

        # Add input, output and memory options to their layout
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        IO_and_options.addWidget(Input(self), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        IO_and_options.addWidget(Output(self), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        IO_and_options.addWidget(OptionsContainer(self), 1)
        IO_and_options.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))   # Vertical
        return layout

    def setSplitter(self):
        cmResizer: QSplitter = QSplitter(self)
        #cmResizer.splitterMoved.connect(lambda: DataBase.ON_SPLITTER_MOVE.setValue(True))
        cmResizer.splitterMoved.connect(lambda: EventRegister.send(EditorResizeEvent(), "Tab"))
        cmResizer.setOrientation(Qt.Horizontal)
        cmResizer.setObjectName("Mem-CodeSplitter")
        cmResizer.setHandleWidth(7)
        cmResizer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        cmResizer.addWidget(EditorWrapper(self))
        cmResizer.addWidget(Memory(self))
        cmResizer.setSizes([INTEGER_MAX, INTEGER_MAX])
        cmResizer.setStretchFactor(0, 1)
        cmResizer.setStretchFactor(1, 1)
        return cmResizer


class MainWidget(MainWidgetGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MainWidget")