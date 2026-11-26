from PyQt5.QtCore import Qt, QRect, QSize, QPointF
from PyQt5.QtGui import QIcon, QPalette
from PyQt5.QtWidgets import QSizePolicy, QStyle, QStyleOptionButton, QStylePainter

from source.comms import Database
from source.filesystem import find_path
from source.interface.editor.me_system.Menu import HiddenTabList
from source.interface.editor.me_system.TabList import TabList
from source.interface.templates import GenericButton, Tooltip


class TabButton(GenericButton):
    """Overflow button that opens the menu of the hidden tabs"""

    def __init__(self, parent):
        super().__init__(parent)
        self.___menu: HiddenTabList = HiddenTabList(self)
        self.___icon_center = None
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

    ___ICON_TEXT_GAP = 4

    def paintEvent(self, event):
        """
        Draw the icon and the counter centered on the same line.
        QPushButton centers the text box, whose blank space below the digits pushes the "+N" off the icon's center,
        so the counter is centered on its own glyphs instead.
        """
        option = QStyleOptionButton()
        self.initStyleOption(option)
        option.text = ""
        option.icon = QIcon()
        painter = QStylePainter(self)
        painter.drawControl(QStyle.CE_PushButton, option)

        contents = self.style().subElementRect(QStyle.SE_PushButtonContents, option, self)
        text = self.text()
        metrics = self.fontMetrics()
        glyphs = metrics.tightBoundingRect(text)
        icon_size = self.iconSize()
        width = icon_size.width() + (self.___ICON_TEXT_GAP + glyphs.width() if text else 0)
        left = contents.x() + (contents.width() - width) / 2
        center = contents.y() + contents.height() / 2

        # Both centers are snapped to whole pixels the same way, so the chevron and the digits share their middle.
        baseline = round(center - (glyphs.top() + glyphs.height() / 2))
        text_center = baseline + (glyphs.top() + glyphs.height() / 2)
        icon_top = round(text_center - self.___iconVisibleCenter(icon_size)) if text else round(center - icon_size.height() / 2)
        icon_rect = QRect(round(left), icon_top, icon_size.width(), icon_size.height())
        self.icon().paint(painter, icon_rect, Qt.AlignCenter, QIcon.Normal if self.isEnabled() else QIcon.Disabled)
        if text:
            painter.setPen(self.palette().color(QPalette.ButtonText))
            painter.drawText(QPointF(icon_rect.right() + 1 + self.___ICON_TEXT_GAP - glyphs.left(), baseline), text)

    def ___iconVisibleCenter(self, size: QSize) -> float:
        """ Vertical middle of the drawn pixels of the icon, from its top, at the given size """
        if self.___icon_center is None or self.___icon_center[0] != size:
            image = self.icon().pixmap(size).toImage()
            rows = [y for y in range(image.height()) if any(image.pixelColor(x, y).alpha() > 64 for x in range(image.width()))]
            middle = (rows[0] + rows[-1] + 1) / 2 if rows else size.height() / 2
            self.___icon_center = (size, middle * size.height() / max(image.height(), 1))
        return self.___icon_center[1]

    def count(self):
        return self.___menu.count()

    def reload(self, tl: TabList):
        """Fill the menu with the tabs outside the visible area of the tab list"""
        # Imported on use: the tab package loads TabManager, which imports this button from the multi-editor system.
        from source.interface.editor.me_system.tab import Tab

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


