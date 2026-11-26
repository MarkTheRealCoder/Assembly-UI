from PyQt5.QtCore import QSize, QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QSizePolicy

from source.comms import Database
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import IconManager
from source.interface import createLayout
from source.interface.editor.me_system.tab.Icon import TabIcon
from source.interface.editor.me_system.tab.Label import TabLabel
from source.interface.templates import Tooltip, CloseButton

# TabManager is 44 px high, and its list uses 1 px for the bottom separator.
TAB_HEIGHT = 43
TAB_MIN_WIDTH = 150
TAB_MAX_WIDTH = 250


class TabGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("Tab")
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self.setFixedHeight(TAB_HEIGHT)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)

        self._tooltip = Tooltip(self, "Tab Tooltip")
        self._tooltip.setPosition("below", "center")
        self._tooltip.setFollowing("widget")
        self._tooltip.setSpecific("Tab")

    def sizeHint(self) -> QSize:
        layout = self.layout()
        width = layout.totalSizeHint().width() if layout is not None else TAB_MIN_WIDTH
        return QSize(max(TAB_MIN_WIDTH, min(TAB_MAX_WIDTH, width)), TAB_HEIGHT)

    def minimumSizeHint(self) -> QSize:
        # The scroll area must keep each tab at the width of its name.
        return self.sizeHint()

    def setupLayout(self, name: str, ext: str, tab_id: int):
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        icon = TabIcon(self, ext)
        label = TabLabel(self, name)
        close = CloseButton(self, "Tab", {"tab": True}).setEventIdentifiers(id=tab_id)
        for widget in (icon, label, close):
            # The macOS style otherwise adds its own layout margins.
            widget.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        layout.addWidget(icon, alignment=Qt.AlignVCenter)
        layout.addWidget(label)
        layout.addWidget(close, alignment=Qt.AlignVCenter)
        self.setLayout(layout)
        self._tooltip.setText(name)
        self.adjustSize()


class TabLogic(TabGraphics):
    def __init__(self, parent, _id: int, name: str, ext: str):
        super().__init__(parent)
        self.___id = _id
        self.___name = name
        self.___ext = ext
        self.___movable = False
        self.___initial_pos_x = None

        self.setupLayout(name, ext, _id)


        Database.ON_TAB_SELECTED.connect(self.selected)

    def getId(self) -> int:
        return self.___id

    def text(self) -> str:
        return self.___name

    def icon(self) -> QIcon:
        return IconManager.getInstance().getIcon(self.___ext)

    def setText(self, text: str):
        self.___name = text
        self.findChild(TabLabel).setText(text)

    def selected(self):
        self.setProperty("marked", Database.ON_TAB_SELECTED.getValue() == self.___id)
        self.style().unpolish(self)
        self.style().polish(self)

    def eventFilter(self, obj, event: QEvent):
        if event.type() == QEvent.MouseMove and self.___movable:
            variation = 0
            if event.pos().x() >= self.___initial_pos_x + 63:
                variation = -1
            elif event.pos().x() <= self.___initial_pos_x - 125:
                variation = 1
            self.setCursor(Qt.ClosedHandCursor)
            self.parent().moveTab(self, variation)
        elif hasattr(event, "button") and event.button() == Qt.LeftButton:
            if event.type() == QEvent.MouseButtonPress:
                self.___movable = True
                self.___initial_pos_x = event.pos().x()
            elif event.type() == QEvent.MouseButtonRelease:
                Database.ON_TAB_SELECTED.setValue(self.___id)
                self.___movable = False
                self.setCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)


class Tab(TabLogic):
    """Tab of an open file, closed through the ClosingEvent addressed to its id"""

    def __init__(self, parent, _id: int, name: str, ext: str):
        super().__init__(parent, _id, name, ext)
        EventRegister.mregister(self, ClosingEvent, "Tab", EventRegister.LOW, id=_id)

    def event(self, event: QEvent):
        return super().event(event)

    def onClosingEvent(self, event: ClosingEvent):
        Database.ON_TAB_CLOSE.setValue(self.getId())
        self.deleteLater()


