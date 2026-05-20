from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QSplitter, QSizePolicy, QVBoxLayout

from source.comms.events import EditorResizeEvent
from source.comms.handlers import EventRegister
from source.interface.debugger import ExecutionContext
from source.interface.editor import EditorWrapper
from source.interface.shared import createLayout
from source.interface.titlebar import Toolbar

INTEGER_MAX = 2147483647


class MainWidgetGraphics(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.resize(parent.size())
        self.setMainLayout()
        self.setObjectName("MainSupportWidget")

    def setMainLayout(self):
        widget = self
        widget.setObjectName("MainWidget")
        layout: QVBoxLayout = createLayout(QVBoxLayout, widget)
        layout.addWidget(Toolbar(widget), 0)
        layout.addWidget(self.setSplitter(widget), 1)
        widget.setLayout(layout)

    def setSplitter(self, widget):
        cmResizer: QSplitter = QSplitter(widget)
        cmResizer.splitterMoved.connect(lambda: EventRegister.send(EditorResizeEvent(), "Tab"))
        cmResizer.setOrientation(Qt.Horizontal)
        cmResizer.setObjectName("Mem-CodeSplitter")
        cmResizer.setHandleWidth(7)
        cmResizer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        ew = EditorWrapper(widget)
        ec = ExecutionContext(widget)

        cmResizer.addWidget(ew)
        cmResizer.addWidget(ec)
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
