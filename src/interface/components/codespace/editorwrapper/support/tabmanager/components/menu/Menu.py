from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QSizePolicy, QWidgetAction

from src.interface.components.codespace.editorwrapper.support.tabmanager.components.menu.components.Container import \
    Container
from src.signals.Variables import DataBase


class HiddenTabList(QMenu):
    def __init__(self, parent):
        super().__init__(parent)
        self.configurations()

        DataBase.ON_TAB_CLOSE.connect(self.hide)
        DataBase.ON_TAB_SELECTED.connect(self.hide)

    def configurations(self):
        self.setObjectName("HiddenTabList")
        self.setContentsMargins(0, 0, 0, 0)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Expanding)

    def addTab(self, _id: int, name: str, icon: QIcon):
        action = QWidgetAction(self)
        action.setDefaultWidget(Container(self, _id, name, icon))
        self.addAction(action)

    def clearActions(self):
        for a in self.actions():
            self.removeAction(a)

    def count(self):
        return len(self.actions())

