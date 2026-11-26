from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QVBoxLayout

from source.interface import createLayout
from source.interface.debugger.mem.ContextWindow import ContextWindow


class ContextContainerGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ContextContainer")
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        # The windows keep their own height and stack from the top.
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def addContextToLayout(self, context_window):
        """ Add a new context window to the container """
        self.layout().addWidget(context_window)


class ContextContainerLogic(ContextContainerGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self.___context_windows: dict[str, ContextWindow] = {}

    def addContext(self, name: str):
        """ Add a new context window to the container with a specific name """
        if name in self.___context_windows:
            return
        context_window = ContextWindow(self, name)
        self.___context_windows[name] = context_window
        self.addContextToLayout(context_window)

    def findContext(self, name: str):
        """ Return the context window with the given name, or None """
        return self.___context_windows.get(name, None)

    def reset(self):
        """ Delete all context windows """
        for context_window in self.___context_windows.values():
            context_window.hide()
            context_window.deleteLater()
        self.___context_windows.clear()


class ContextContainer(ContextContainerLogic):
    def __init__(self, parent):
        super().__init__(parent)
