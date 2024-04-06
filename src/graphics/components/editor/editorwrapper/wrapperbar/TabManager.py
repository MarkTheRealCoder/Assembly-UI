from PyQt5.QtCore import QSize, Qt, QEvent
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QTabBar, QTabWidget, QSizePolicy


class TabManager(QTabBar):
    def __init__(self, parent: QTabWidget):
        super().__init__(parent)
        self.configurations()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setIconSize(QSize(20, 20))
        self.setFixedHeight(30)
        self.setAcceptDrops(False)
        self.setExpanding(True)
        self.setTabsClosable(True)
        self.setUsesScrollButtons(False)
        self.setMovable(True)
        self.setAutoFillBackground(True)
        self.setElideMode(Qt.ElideRight)





