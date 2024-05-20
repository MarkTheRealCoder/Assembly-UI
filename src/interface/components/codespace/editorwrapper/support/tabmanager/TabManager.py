from PyQt5.QtWidgets import QSizePolicy, QFrame, QHBoxLayout, QApplication

from src.eventhandlers.Register import EventRegister
from src.events.data.NoTabEvent import NoTabEvent
from src.events.graphic.EditorResizeEvent import EditorResizeEvent
from src.events.graphic.TabAddedEvent import TabAddedEvent
from src.events.graphic.TabListScrollEvent import TabListScrollEvent
from src.interface.commons.Commons import createLayout
from src.interface.components.codespace.editorwrapper.support.tabmanager.components.TabButton import TabButton
from src.interface.components.codespace.editorwrapper.support.tabmanager.components.TabList import TabList
from src.interface.components.codespace.editorwrapper.support.tabmanager.tab.Tab import Tab
from src.signals.Variables import DataBase


@EventRegister.register(EditorResizeEvent, "Tab", EventRegister.HIGH)
@EventRegister.register(TabListScrollEvent, "Tab", EventRegister.HIGH)
@EventRegister.register(TabAddedEvent, "Tab", EventRegister.HIGH)
class TabManager(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.___layout: QHBoxLayout = None
        self.___list: TabList = None
        self.___emergency: TabButton = TabButton(self)

        self.configurations()

    def configurations(self):
        self.setObjectName("TabManager")
        self.setFixedHeight(40)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)

        self.___list = TabList(self)
        self.___layout: QHBoxLayout = createLayout(QHBoxLayout, self)

        self.___layout.addWidget(self.___list)
        self.setLayout(self.___layout)

    def addOverflowButton(self):
        self.___emergency.reload(self.___list)
        if self.___emergency.count() == 0:
            self.___layout.removeWidget(self.___emergency)
        else:
            if self.___emergency not in self.___layout.children():
                self.___layout.addWidget(self.___emergency)

        self.update()

    def addTab(self, _id: int, name: str, ext: str):
        self.___list.addTab(_id, name, ext)

    def isFirst(self):
        return self.___list.count() == 1

    def setActiveTab(self, _id: int = None):
        if _id is not None:
            DataBase.ON_TAB_SELECTED.setValue(_id)
        elif self.___list.count() > 1:
            layout = self.___list.widget().layout()
            indx = 0
            _id = DataBase.ON_TAB_CLOSE.getValue()
            for tab in self.___list.findChildren(Tab):
                if tab.getId() == _id:
                    indx = layout.indexOf(tab)
            indx = 1 if indx == 0 else 0
            DataBase.ON_TAB_SELECTED.setValue(layout.itemAt(indx).widget().getId())
        else:
            QApplication.instance().postEvent(self.parent(), NoTabEvent())
            DataBase.ON_TAB_SELECTED.setValue(0)

    def onClosingEvent(self, e):
        self.addOverflowButton()

    def onTabListScrollEvent(self, e):
        self.addOverflowButton()

    def onTabAddedEvent(self, e):
        self.addOverflowButton()

    def onEditorResizeEvent(self, e):
        self.addOverflowButton()

