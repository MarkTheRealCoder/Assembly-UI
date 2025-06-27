from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QSizePolicy, QFrame, QHBoxLayout

from source.comms.events import TabListScrollEvent
from source.comms.handlers import EventRegister
from source.interface.editor.me_system.tab.Tab import Tab
from source.interface.shared import createLayout


class TabList(QScrollArea):
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
        self.widget().addTab(Tab(self.widget(), _id, name, ext))
        self.update()

    def count(self):
        return self.widget().layout().count()

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
        layout.addWidget(tab, 1)

    def moveTab(self, target, v):

        indx = self.layout().indexOf(target) - v

        self.layout().removeWidget(target)

        if indx < 0:
            indx = 0
        elif indx >= self.layout().count():
            indx = self.layout().count()

        self.layout().insertWidget(indx, target, 1)
        self.update()
