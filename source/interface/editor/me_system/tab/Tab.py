from PyQt5.QtCore import QSize, QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QLayout

from source.comms.Signals import DataBase
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem.IconManager import IconManager
from source.interface.editor.me_system.tab.Icon import TabIcon
from source.interface.editor.me_system.tab.Label import TabLabel
from source.interface.shared import createLayout
from source.interface.templates import Tooltip
from source.interface.templates.CloseButton import CloseButton


class TabGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("Tab")
        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self.setMinimumWidth(150)
        self.setMaximumWidth(250)
        self.setFixedHeight(44)
        self.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

        self._tooltip = Tooltip(self, "Tab Tooltip")
        self._tooltip.setPosition("below", "center")
        self._tooltip.setFollowing("widget")
        self._tooltip.setSpecific("Tab")

    def sizeHint(self) -> QSize:
        return QSize(150, 44)

    def setupLayout(self, name: str, ext: str, tab_id: int):
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.setSizeConstraint(QLayout.SetFixedSize)
        layout.addWidget(TabIcon(self, ext))
        layout.addWidget(TabLabel(self, name))
        layout.addWidget(CloseButton(self, "Tab", {"tab": True})
                         .setEventIdentifiers(id=tab_id))
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
        self.installEventFilter(self)

        DataBase.ON_TAB_SELECTED.connect(self.selected)

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
        self.setProperty("marked", DataBase.ON_TAB_SELECTED.getValue() == self.___id)
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
                DataBase.ON_TAB_SELECTED.setValue(self.___id)
                self.___movable = False
                self.setCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)


class Tab(TabLogic):
    def __init__(self, parent, _id: int, name: str, ext: str):
        super().__init__(parent, _id, name, ext)
        EventRegister.mregister(self, ClosingEvent, "Tab", EventRegister.LOW, id=_id)

    def event(self, event: QEvent):
        return super().event(event)

    def onClosingEvent(self, event: ClosingEvent):
        print("Closing tab", self.getId())
        DataBase.ON_TAB_CLOSE.setValue(self.getId())
        self.deleteLater()

    def mousePressEvent(self, a0):
        print(self.size())
        super().mousePressEvent(a0)



