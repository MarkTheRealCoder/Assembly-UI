from PyQt5.QtCore import Qt, QRect, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy

from source.comms import Database
from source.filesystem import find_path
from source.interface.editor.me_system.Menu import HiddenTabList
from source.interface.editor.me_system.TabList import TabList
from source.interface.editor.me_system.tab.Tab import Tab
from source.interface.templates import GenericButton, Tooltip


class TabButton(GenericButton):
    """Overflow button that opens the menu of the hidden tabs"""

    def __init__(self, parent):
        super().__init__(parent)
        self.___menu: HiddenTabList = HiddenTabList(self)
        self.tooltip = Tooltip(self, "Hidden files")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)
        self.configurations()

    def configurations(self):
        self.setObjectName("TabButton")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        self.setCursor(Qt.PointingHandCursor)
        self.setIcon(self.rerenderIcon(QIcon(find_path("arrow-down.svg")), "#FFFFFF"))
        self.setIconSize(QSize(14, 14))
        self.setMenu(self.___menu)

    def count(self):
        return self.___menu.count()

    def reload(self, tl: TabList):
        """Fill the menu with the tabs outside the visible area of the tab list"""
        self.___menu.hide()
        self.___menu.clearActions()
        panel = tl.widget()
        viewport = tl.viewport()
        visible = QRect(-panel.x(), 0, viewport.width(), viewport.height())
        tabs = tl.findChildren(Tab)
        for tab in tabs:
            if not visible.intersects(tab.geometry()) and tab.getId() != Database.ON_TAB_CLOSE.getValue():
                self.___menu.addTab(tab.getId(), tab.text(), tab.icon())
        count = self.count()
        self.setText(f"+{count}")
        self.tooltip.setText(f"{count} hidden file{'' if count == 1 else 's'}")


