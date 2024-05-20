from PyQt5.QtCore import QSize, QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout

from src.eventhandlers.Register import EventRegister
from src.events.data.ClosingEvent import ClosingEvent
from src.filesystem.IconManager import IconManager
from src.filesystem.documents.FileTypes import FT
from src.interface.commons.Commons import createLayout
from src.interface.commons.globals.CloseButton import CloseButton
from src.interface.components.codespace.editorwrapper.support.tabmanager.tab.components.Icon import TabIcon
from src.interface.components.codespace.editorwrapper.support.tabmanager.tab.components.Label import TabLabel
from src.signals.Variables import DataBase


class Tab(QFrame):
    def __init__(self, parent, _id: int, name: str, ext: str):
        super().__init__(parent)

        self.___id = _id
        self.___name = name
        self.___ext = ext

        self.___movable = False
        self.___initial_pos_x = None

        self.configurations(name, ext)

        DataBase.ON_TAB_SELECTED.connect(self.selected)
        EventRegister.mregister(self, ClosingEvent, "Tab", EventRegister.LOW, id=self.___id)

    def configurations(self, name, ext):
        self.setObjectName("Tab")
        self.setFixedSize(QSize(150, 40))
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)

        layout.addWidget(TabIcon(self, ext))
        layout.addWidget(TabLabel(self, name))
        layout.addWidget(CloseButton.preset(self, "TAB", "Tab", True)
                         .setEventIdentifiers(id=self.___id))
        self.setLayout(layout)

        self.setToolTip(self.___name)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

        self.installEventFilter(self)

    def getId(self) -> int:
        return self.___id

    def text(self) -> str:
        return self.___name

    def icon(self) -> QIcon:
        return IconManager.getInstance().getIcon(self.___ext)

    def event(self, event: QEvent):
        return super().event(event)

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
                DataBase.DOCTYPE.setValue(int(FT.findByExt(self.___ext)))
                self.___movable = False
                self.setCursor(Qt.ArrowCursor)

        return super().eventFilter(obj, event)

    def selected(self):
        self.setProperty("marked", DataBase.ON_TAB_SELECTED.getValue() == self.___id)
        self.style().unpolish(self)
        self.style().polish(self)

    def setText(self, text: str):
        self.___name = text
        self.findChild(TabLabel).setText(text)

    def onClosingEvent(self, event: ClosingEvent):
        print("Closing tab", self.___id)
        self.deleteLater()


