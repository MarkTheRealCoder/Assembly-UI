from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QMouseEvent, QClipboard
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QMenu, QSizePolicy, QLayout, QFrame, QSpacerItem

from src.graphics.components.external.paths.PathTree import PathTree
from src.graphics.components.globals.CloseButton import CloseButton
from src.graphics.components.globals.TopFrame import TopFrame
from src.graphics.components.trash.TrashWindow import wOpen
from src.tools.Tools import open_dir, find_path as find_icon
from src.tools.Variables import DataBase as db


class ToolBar(QFrame):

    def __init__(self, mwt: QWidget, app: QClipboard):
        super().__init__(mwt)
        self.___clipboard: QClipboard = app
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
        layout.addWidget(RunButton(self), 2)
        layout.addWidget(ApplicationLabel(self, self.mw, self.___clipboard), 30)
        layout.addWidget(MinimizeButton(self, self.mw), 2)
        layout.addSpacerItem(QSpacerItem(1, 15, QSizePolicy.Fixed, QSizePolicy.Fixed))
        clsbtn = CloseButton(self, self.mw, False)
        clsbtn.addSignal(db.CLOSING_MAIN_WINDOW)
        layout.addWidget(clsbtn, 2)
        self.setLayout(layout)


class IconButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        icon_size: QSize = QSize()
        size = 20
        icon_size.setHeight(size)
        icon_size.setWidth(size)
        icon = QIcon(find_icon("Logo.png"))
        self.setIcon(icon)
        self.setIconSize(icon_size)
        self.setObjectName("Icon")
        self.setFixedSize(size+15, size+14)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.___event_enabled = True

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)


class FileMenu(QPushButton):
    def __init__(self, parent):
        super(FileMenu, self).__init__(parent)
        self.setText(" File")
        self.setObjectName("File")
        self.configure()
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Change Working Path", lambda: wOpen(self.parent().mw, PathTree()))
        menu.addSeparator()
        menu.addAction("Open", lambda: wOpen(self.parent().mw, PathTree(True)))
        menu.addAction("New")
        menu.addSeparator()
        menu.addAction("Save as...")
        self.setMenu(menu)


class HelpMenu(QPushButton):
    def __init__(self, parent):
        super(HelpMenu, self).__init__(parent)
        self.setText(" Help")
        self.setObjectName("Help")
        self.configure()
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Features")
        menu.addSeparator()
        menu.addAction("8088 Instructions")
        menu.addAction("IJVM Instructions")
        self.setMenu(menu)


class RunButton(QPushButton):
    def __init__(self, parent):
        super(RunButton, self).__init__(None)
        self.setParent(parent)
        self.setText("▶")
        self.setObjectName("Run")
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)


class MinimizeButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super(MinimizeButton, self).__init__(parent)
        self.mainwindow = mw
        self.setIcon(QIcon(find_icon("minimize.png")))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Minimize")
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        self.mainwindow.showMinimized()


class ApplicationLabel(TopFrame):
    def __init__(self, parent, mw: QMainWindow, clip: QClipboard = None):
        super().__init__(parent, mw)
        db.FOLDER.connect(self.setLabel)
        self.setAlignment(Qt.AlignCenter)

        self.clipboard = clip
        self.___curr_dir = None

        self.setLabel()

        self.setActionOn("LeftDoubleClick", lambda: self.clipboard.setText(self.___curr_dir, mode=self.clipboard.Clipboard))
        self.setActionOn("LeftCtrlClick", lambda: open_dir(self.___curr_dir))

    def setLabel(self):
        self.___curr_dir = db.FOLDER.getValue()
        self.setText(f"Assembly Stdio - {self.___curr_dir}")

