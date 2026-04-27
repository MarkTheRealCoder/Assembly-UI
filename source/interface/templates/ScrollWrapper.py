from typing import Literal

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QWidget, QFrame


class ScrollWrapperGraphics(QScrollArea):
    def __init__(self, parent, widget):
        super().__init__(parent)
        self.setObjectName("ScrollWrapper")
        self.setWidgetResizable(True)
        self.setFrameShape(QFrame.Shape.Panel)
        self.setWidget(widget(self))


class ScrollWrapperLogic(ScrollWrapperGraphics):
    def __init__(self, parent, widget):
        super().__init__(parent, widget)
        # Implementation of scroll wrapper logic goes here
        self.___widget = self.widget()

    def exposeWidget(self) -> QWidget:
        """ Expose the widget contained in the scroll wrapper to allow for direct interaction with it.
        """
        return self.___widget


class ScrollWrapper(ScrollWrapperLogic):
    SBO = Literal["as_needed", "always_on", "always_off"]
    scrollbaroptions = {
        "as_needed": Qt.ScrollBarPolicy.ScrollBarAsNeeded,
        "always_on": Qt.ScrollBarPolicy.ScrollBarAlwaysOn,
        "always_off": Qt.ScrollBarPolicy.ScrollBarAlwaysOff
    }
    def __init__(self, parent, widget, vscrollbar_policy: SBO = "always_off", hscrollbar_policy: SBO = "always_off"):
        super().__init__(parent, widget)
        # Additional initialization for ScrollWrapper
        self.setHorizontalScrollBarPolicy(self.scrollbaroptions.get(hscrollbar_policy, Qt.ScrollBarPolicy.ScrollBarAlwaysOff))
        self.setVerticalScrollBarPolicy(self.scrollbaroptions.get(vscrollbar_policy, Qt.ScrollBarPolicy.ScrollBarAlwaysOff))