from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy

from source.comms import Database
from source.filesystem import find_path
from source.interface.editor.me_system.Menu import HiddenTabList
from source.interface.editor.me_system.TabList import TabList
from source.interface.editor.me_system.tab.Tab import Tab
from source.interface.templates import GenericButton


class TabButton(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.___menu: HiddenTabList = HiddenTabList(self)
        self.configurations()

    def configurations(self):
        self.setObjectName("TabButton")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(self.rerenderIcon(QIcon(find_path("arrow-down.svg")), "#569CD6"))
        self.setIconSize(QSize(15, 15))
        self.setMenu(self.___menu)

    def count(self):
        return self.___menu.count()

    def reload(self, tl: TabList):
        self.___menu.hide()
        self.___menu.clearActions()
        vr = tl.widget().visibleRegion()
        tabs = tl.findChildren(Tab)
        for tab in tabs:
            if not vr.contains(tab.geometry()) and tab.getId() != Database.ON_TAB_CLOSE.getValue():
                self.___menu.addTab(tab.getId(), tab.text(), tab.icon())









