from PyQt5.QtWidgets import QFrame, QSizePolicy


class MemoryViewerGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MemoryViewer")
        # Additional UI setup can be done here
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)


class MemoryViewerLogic(MemoryViewerGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of memory viewer logic goes here


class MemoryViewer(MemoryViewerLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for MemoryViewer