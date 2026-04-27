from PyQt5.QtWidgets import QFrame, QVBoxLayout

from source.interface.debugger.mem.ContextWindow import ContextWindow
from source.interface.shared import createLayout


class ContextContainerGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("ContextContainer")
        # Additional UI setup can be done here
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        self.setLayout(layout)

    def addContextToLayout(self, context_window):
        """ Add a new context window to the container """
        self.layout().addWidget(context_window)


class ContextContainerLogic(ContextContainerGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of context container logic goes here
        self.___context_windows: dict[str: ContextWindow] = {}

    def addContext(self, name: str):
        """ Add a new context window to the container with a specific name """
        context_window = ContextWindow(self, name)
        self.___context_windows[name] = context_window
        self.addContextToLayout(context_window)

    def findContext(self, name: str):
        return self.___context_windows.get(name, None)

    def reset(self):
        """ Empty the context window """
        self.___context_windows.clear()
        old_layout = self.layout()
        old_layout.deleteLater()
        new_layout = createLayout(QVBoxLayout, self)
        self.setLayout(new_layout)


class ContextContainer(ContextContainerLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for ContextContainer
