from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QSizePolicy, QFrame, QHBoxLayout

from source.comms.events import TabListScrollEvent
from source.comms.handlers import EventRegister
from source.interface import createLayout


class TabList(QScrollArea):
    """Horizontally scrollable strip of tabs"""

    def __init__(self, parent):
        super().__init__(parent)
        self.configurations()
        self.setWidget(_Support(self))

    def configurations(self):
        self.setObjectName("TabList")
        self.setWidgetResizable(True)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setContentsMargins(0, 0, 0, 0)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.horizontalScrollBar().setObjectName("TabListScrollBar")

    def addTab(self, _id: int, name: str, ext: str):
        # Imported on use: the tab package loads TabManager, which imports this list from the multi-editor system.
        from source.interface.editor.me_system.tab import Tab

        self.widget().addTab(Tab(self.widget(), _id, name, ext))
        self.update()

    def count(self):
        return self.widget().count()

    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        scroll_bar = self.horizontalScrollBar()
        scroll_bar.setValue(scroll_bar.value() - delta)
        EventRegister.send(TabListScrollEvent(), "Tab")


class _Support(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.configurations()

    def configurations(self):
        self.setObjectName("TabListPanel")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.setAlignment(Qt.AlignLeft)
        self.setLayout(layout)

    def addTab(self, tab):
        layout: QHBoxLayout = self.layout()     # noqas
        layout.addWidget(tab)

    def count(self):
        return self.layout().count()

    def moveTab(self, target, v):
        """Move a tab by v positions towards the start, clamped to the list"""

        indx = self.layout().indexOf(target) - v

        self.layout().removeWidget(target)

        if indx < 0:
            indx = 0
        elif indx >= self.layout().count():
            indx = self.layout().count()

        self.layout().insertWidget(indx, target)
        self.update()
