from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QSizePolicy

from src.filesystem.Folder import find_path
from src.interface.components.codespace.editorwrapper.support.tabmanager.components.TabList import TabList
from src.interface.components.codespace.editorwrapper.support.tabmanager.components.menu.Menu import HiddenTabList
from src.interface.components.codespace.editorwrapper.support.tabmanager.tab.Tab import Tab
from src.signals.Variables import DataBase


class TabButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.___menu: HiddenTabList = HiddenTabList(self)
        self.configurations()

    def configurations(self):
        self.setObjectName("TabButton")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(QIcon(find_path("drop-down-arrow.png")))
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
            if not vr.contains(tab.geometry()) and tab.getId() != DataBase.ON_TAB_CLOSE.getValue():
                self.___menu.addTab(tab.getId(), tab.text(), tab.icon())









