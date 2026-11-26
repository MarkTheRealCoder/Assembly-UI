from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QSizePolicy, QFrame, QHBoxLayout, QApplication

from source.comms import Database
from source.comms.events import EditorResizeEvent, NoTabEvent, TabAddedEvent, TabListScrollEvent
from source.comms.handlers import EventRegister
from source.interface import createLayout
from source.interface.editor.me_system import TabButton, TabList
from source.interface.editor.me_system.tab.Tab import Tab


@EventRegister.register(EditorResizeEvent, "Tab", EventRegister.HIGH)
@EventRegister.register(TabListScrollEvent, "Tab", EventRegister.HIGH)
@EventRegister.register(TabAddedEvent, "Tab", EventRegister.HIGH)
class TabManager(QFrame):
    """Tab bar with the tab list and the overflow button for hidden tabs"""

    def __init__(self, parent):
        super().__init__(parent)
        self.___layout: QHBoxLayout = None
        self.___list: TabList = None
        self.___emergency: TabButton = TabButton(self)
        self.___emergency.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)
        self.___emergency.hide()

        # Tabs change geometry only after Qt processes the layout and deferred deletes.
        self.___overflow_timer = QTimer(self)
        self.___overflow_timer.setSingleShot(True)
        self.___overflow_timer.setInterval(30)
        self.___overflow_timer.timeout.connect(self.addOverflowButton)

        self.configurations()
        Database.ON_TAB_CLOSE.connect(self.scheduleOverflowUpdate)

    def configurations(self):
        self.setObjectName("TabManager")
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setContentsMargins(0, 0, 0, 0)

        self.___list = TabList(self)
        self.___layout: QHBoxLayout = createLayout(QHBoxLayout, self)

        self.___layout.addWidget(self.___list)
        self.___layout.addWidget(self.___emergency)
        self.setLayout(self.___layout)

    def scheduleOverflowUpdate(self):
        self.___overflow_timer.start()

    def addOverflowButton(self):
        if not self.isVisible():
            return
        self.___emergency.reload(self.___list)
        overflow = self.___emergency.count() > 0
        if overflow != self.___emergency.isVisibleTo(self):
            # The button changes the width of the list, so the hidden tabs must be recomputed.
            self.___emergency.setVisible(overflow)
            self.___layout.activate()
            self.___emergency.reload(self.___list)

        self.update()

    def addTab(self, _id: int, name: str, ext: str):
        self.___list.addTab(_id, name, ext)

    def isFirst(self):
        return self.___list.count() == 1

    def setActiveTab(self, _id: int = None):
        """Select the given tab, or a neighbor of the closed one, or clear the selection"""
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
        self.scheduleOverflowUpdate()

    def onTabListScrollEvent(self, e):
        self.scheduleOverflowUpdate()

    def onTabAddedEvent(self, e):
        self.scheduleOverflowUpdate()

    def onEditorResizeEvent(self, e):
        self.scheduleOverflowUpdate()

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.scheduleOverflowUpdate()

    def showEvent(self, event):
        super().showEvent(event)
        self.scheduleOverflowUpdate()


