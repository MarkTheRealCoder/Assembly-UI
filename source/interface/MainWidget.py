from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSplitter, QSizePolicy, QVBoxLayout, QHBoxLayout, QSpacerItem

from source.comms.events import EditorResizeEvent
from source.comms.handlers import EventRegister
from source.interface.debugger import ExecutionContext
from source.interface.editor import EditorWrapper
from source.interface.shared import createLayout, makeResizingLayout
from source.interface.titlebar import Toolbar

INTEGER_MAX = 2147483647


class MainWidgetGraphics(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(parent.size())
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setMainLayout()
        self.setObjectName("MainSupportWidget")
        self.setAttribute(Qt.WA_TranslucentBackground, True)

    def setMainLayout(self):
        widget = makeResizingLayout(self)
        widget.setObjectName("MainWidget")
        layout: QVBoxLayout = createLayout(QVBoxLayout, widget)
        layout.addWidget(Toolbar(widget), 0)
        self.buildCoreComponents(layout, widget)
        widget.setLayout(layout)

    def buildCoreComponents(self, layout: QVBoxLayout, widget):
        layout.setAlignment(Qt.AlignTop | Qt.AlignCenter)

        code_and_memory: QHBoxLayout = createLayout(QHBoxLayout, widget)

        # Add to main layout
        layout.addLayout(code_and_memory)
        layout.addSpacerItem(QSpacerItem(0, 7, QSizePolicy.Expanding, QSizePolicy.Fixed))

        # Add code and memory to their H layout
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))
        code_and_memory.addWidget(self.setSplitter(widget), 1)
        code_and_memory.addSpacerItem(QSpacerItem(7, 0, QSizePolicy.Fixed, QSizePolicy.Expanding))
        return layout

    def setSplitter(self, widget):
        cmResizer: QSplitter = QSplitter(widget)
        cmResizer.splitterMoved.connect(lambda: EventRegister.send(EditorResizeEvent(), "Tab"))
        cmResizer.setOrientation(Qt.Horizontal)
        cmResizer.setObjectName("Mem-CodeSplitter")
        cmResizer.setHandleWidth(7)
        cmResizer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        cmResizer.addWidget(EditorWrapper(widget))
        cmResizer.addWidget(ExecutionContext(widget)) # todo change to Memory(self) when implemented
        cmResizer.setSizes([INTEGER_MAX, INTEGER_MAX])
        cmResizer.setStretchFactor(0, 1)
        cmResizer.setStretchFactor(1, 1)
        return cmResizer


class MainWidgetLogic(MainWidgetGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class MainWidget(MainWidgetLogic):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)




"""


"""