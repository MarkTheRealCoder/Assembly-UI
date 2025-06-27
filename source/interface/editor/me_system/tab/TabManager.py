from PyQt5.QtWidgets import QSizePolicy, QFrame, QHBoxLayout, QApplication

from source.comms import Database
from source.comms.events import EditorResizeEvent
from source.comms.events import NoTabEvent
from source.comms.events import TabAddedEvent
from source.comms.events import TabListScrollEvent
from source.comms.handlers import EventRegister
from source.interface.editor.me_system.TabButton import TabButton
from source.interface.editor.me_system.TabList import TabList
from source.interface.editor.me_system.tab.Tab import Tab
from source.interface.shared import createLayout


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
            Database.ON_TAB_SELECTED.setValue(_id)
        elif self.___list.count() > 1:
            layout = self.___list.widget().layout()
            indx = 0
            _id = Database.ON_TAB_CLOSE.getValue()
            for tab in self.___list.findChildren(Tab):
                if tab.getId() == _id:
                    indx = layout.indexOf(tab)
            indx = 1 if indx == 0 else 0
            Database.ON_TAB_SELECTED.setValue(layout.itemAt(indx).widget().getId())
        else:
            QApplication.instance().postEvent(self.parent(), NoTabEvent())
            Database.ON_TAB_SELECTED.setValue(0)

    def onClosingEvent(self, e):
        self.addOverflowButton()

    def onTabListScrollEvent(self, e):
        self.addOverflowButton()

    def onTabAddedEvent(self, e):
        self.addOverflowButton()

    def onEditorResizeEvent(self, e):
        self.addOverflowButton()


# TODO : fix circular import and bad module design

