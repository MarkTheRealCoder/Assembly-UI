from source.interface.templates import GenericButton


class DebuggerButton(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("DebuggerButton")

    def set_icon(self, icon):
        self.setIcon(icon)

    def setAction(self, func: callable, condition: callable = lambda: True):
        self.clicked.connect(lambda: func() if condition() else None)

    def setTag(self, key: str):
        self.setProperty(key, True)
