from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout

from source.comms import Database
from source.interface.editor.me_system.Icon import Icon
from source.interface.editor.me_system.Label import Label
from source.interface.shared import createLayout
from source.interface.templates import CloseButton


class Container(QFrame):
    def __init__(self, parent, _id: int, name: str, icon: QIcon):
        super().__init__(parent)

        self.___id: int = _id

        self.configurations(_id, name, icon)

        self.selected()
        Database.ON_TAB_SELECTED.connect(self.selected)

    def configurations(self, _id: int, name: str, icon: QIcon):
        self.setObjectName("Container")
        self.setFixedSize(150, 25)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.addWidget(Icon(self, icon))
        layout.addWidget(Label(self, name))
        close_button = CloseButton(self, "Tab", {"tab": True}).setEventIdentifiers(id=_id)
        close_button.setFixedSize(QSize(15, 15))
        layout.addWidget(close_button)
        self.setLayout(layout)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

    def mousePressEvent(self, a0):
        Database.ON_TAB_SELECTED.setValue(self.___id)

    def selected(self):
        self.setProperty("marked", Database.ON_TAB_SELECTED.getValue() == self.___id)
        self.style().unpolish(self)
        self.style().polish(self)
