from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout

from src.interface.commons.Commons import createLayout
from src.interface.commons.globals.CloseButton import CloseButton
from src.interface.components.codespace.editorwrapper.support.tabmanager.components.menu.components.Icon import Icon
from src.interface.components.codespace.editorwrapper.support.tabmanager.components.menu.components.Label import Label
from src.signals.Variables import DataBase


class Container(QFrame):
    def __init__(self, parent, _id: int, name: str, icon: QIcon):
        super().__init__(parent)

        self.___id: int = _id

        self.configurations(_id, name, icon)

        self.selected()
        DataBase.ON_TAB_SELECTED.connect(self.selected)

    def configurations(self, _id: int, name: str, icon: QIcon):
        self.setObjectName("Container")
        self.setFixedSize(150, 25)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.addWidget(Icon(self, icon))
        layout.addWidget(Label(self, name))
        layout.addWidget(CloseButton.preset(self, "TAB", "Tab", True, self.___id))
        self.setLayout(layout)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

    def mousePressEvent(self, a0):
        DataBase.ON_TAB_SELECTED.setValue(self.___id)

    def selected(self):
        self.setProperty("marked", DataBase.ON_TAB_SELECTED.getValue() == self.___id)
        self.style().unpolish(self)
        self.style().polish(self)
