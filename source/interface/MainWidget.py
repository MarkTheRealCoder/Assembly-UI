from PyQt5.QtWidgets import QWidget, QVBoxLayout

from source.comms.events import EditorResizeEvent
from source.comms.handlers import EventRegister
from source.interface.debugger import ExecutionContext
from source.interface.editor import EditorWrapper
from source.interface.shared import createLayout, Splitter
from source.interface.titlebar import Toolbar

EDITOR_MIN_WIDTH = 200


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
        cmResizer: Splitter = Splitter(widget, "Mem-CodeSplitter", "layout/editor-debugger-splitter")
        cmResizer.splitterMoved.connect(lambda: EventRegister.send(EditorResizeEvent(), "Tab"))
        ew = EditorWrapper(widget)
        ec = ExecutionContext(widget)

        cmResizer.addPane(ew, EDITOR_MIN_WIDTH)
        cmResizer.addPane(ec, ec.splitterMinimumWidth())
        cmResizer.restoreSizes([1, 1])
        return cmResizer


class MainWidgetLogic(MainWidgetGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class MainWidget(MainWidgetLogic):
    def __init__(self, parent):
        super().__init__(parent)
