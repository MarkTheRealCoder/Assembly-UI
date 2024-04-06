from PyQt5.QtCore import Qt, QSize
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QFrame, QHBoxLayout, QVBoxLayout, QDialog

from src.graphics.components.globals.CloseButton import CloseButton
from src.graphics.components.globals.TopFrame import TopFrame
from src.tools.Tools import find_path as getSS, createLayout, translateQSS, Desktop
from src.tools.Variables import DataBase as db

WINDOW_ACTIVE = None


def wOpen(parent, anywidget, size: QSize = None):
    global WINDOW_ACTIVE
    if WINDOW_ACTIVE is None:
        size = size if size is not None else Desktop.sizeHint(2/5, 3/5)
        WINDOW_ACTIVE = TrashWindow(parent, anywidget, size)
        WINDOW_ACTIVE.show()
        db.TOOL_WINDOW_CLOSED.setValue(False)


class TrashWindow(QDialog):

    def __init__(self, parent, widget, size: QSize):
        super(QDialog, self).__init__(parent)
        self.setObjectName("Trash")
        self.setConfigurations(size)
        self.___widget = widget
        self.frame = QFrame(self)

        self.setMainWidget(widget)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        db.TOOL_WINDOW_CLOSED.connect(self.reset_window_reference)

    def setConfigurations(self, size: QSize):
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)
        self.setWindowModality(Qt.WindowModal)
        self.setMinimumSize(size)
        self.centerOnScreen()

        with open(getSS("style.qss"), "r") as f:
            self.setStyleSheet(translateQSS(f.read()))

    def setMainWidget(self, widget):
        widget.setParent(self)

        ml: QVBoxLayout = createLayout(QVBoxLayout, self.frame)
        tl: QHBoxLayout = createLayout(QHBoxLayout, self.frame)

        ml.addLayout(tl)
        ml.addWidget(widget)

        tl.addWidget(TopFrame(self))
        close = CloseButton(self)
        close.addSignal(db.TOOL_WINDOW_CLOSED)
        tl.addWidget(close)

        tl.setStretch(0, 5)
        tl.setStretch(1, 1)

        self.setLayout(ml)

    def centerOnScreen(self):
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def deleteNow(self):
        db.TOOL_WINDOW_CLOSED.setValue(True)
        self.deleteLater()

    def reset_window_reference(self):
        if db.TOOL_WINDOW_CLOSED.getValue():
            global WINDOW_ACTIVE
            WINDOW_ACTIVE = None
