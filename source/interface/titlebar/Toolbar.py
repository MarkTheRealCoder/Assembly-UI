from PyQt5.QtWidgets import QFrame, QWidget, QSizePolicy, QHBoxLayout, QLayout, QSpacerItem

from source.interface.templates.CloseButton import CloseButton
from source.interface.titlebar.Files import FileMenu
from source.interface.titlebar.Icon import IconButton
from source.interface.titlebar.Maximize import MaximizeButton
from source.interface.titlebar.Minimize import MinimizeButton
from source.interface.titlebar.Title import Title
from source.interface.titlebar.UserHelp import HelpMenu


class Toolbar(QFrame):

    def __init__(self, mwt: QWidget):
        super().__init__(mwt)
        self.mw: QMainWindow = mwt.parent()  # noqas
        self.setObjectName("Toolbar")
        self.setFixedHeight(35)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.addComponents()

    def addComponents(self):
        layout = QHBoxLayout(self)
        layout.setSpacing(0)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        layout.addWidget(IconButton(self), 0)
        layout.addWidget(FileMenu(self), 2)
        layout.addWidget(HelpMenu(self), 2)
        layout.addWidget(Title(self, self.mw), 30)
        layout.addWidget(MinimizeButton(self, self.mw), 2)
        layout.addWidget(MaximizeButton(self, self.mw), 2)
        layout.addSpacerItem(QSpacerItem(1, 15, QSizePolicy.Fixed, QSizePolicy.Fixed))
        layout.addWidget(CloseButton(self), 2)
        self.setLayout(layout)