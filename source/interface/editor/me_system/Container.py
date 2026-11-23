from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QHBoxLayout

from source.comms import Database
from source.interface.editor.me_system.Icon import Icon
from source.interface.editor.me_system.Label import Label
from source.interface.shared import createLayout
from source.interface.templates import CloseButton, Tooltip


class Container(QFrame):
    """Row of the hidden tab menu: icon, name and close button of a tab"""

    def __init__(self, parent, _id: int, name: str, icon: QIcon):
        super().__init__(parent)

        self.___id: int = _id

        self.tooltip = Tooltip(self, name)
        self.tooltip.setPosition("right", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

        self.configurations(_id, name, icon)

        self.selected()
        Database.ON_TAB_SELECTED.connect(self.selected)

    def configurations(self, _id: int, name: str, icon: QIcon):
        self.setObjectName("Container")
        self.setFixedSize(150, 32)
        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        file_icon = Icon(self, icon)
        label = Label(self, name)
        close_button = CloseButton(self, "Tab", {"tab": True}).setEventIdentifiers(id=_id)
        close_button.setFixedSize(QSize(16, 16))
        for widget in (file_icon, label, close_button):
            # The macOS style otherwise adds its own layout margins.
            widget.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        layout.addWidget(file_icon, alignment=Qt.AlignVCenter)
        layout.addWidget(label)
        layout.addWidget(close_button, alignment=Qt.AlignVCenter)
        self.setLayout(layout)

        self.setFrameStyle(QFrame.Panel | QFrame.Raised)

    def mousePressEvent(self, a0):
        Database.ON_TAB_SELECTED.setValue(self.___id)

    def selected(self):
        self.setProperty("marked", Database.ON_TAB_SELECTED.getValue() == self.___id)
        self.style().unpolish(self)
        self.style().polish(self)
