from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon, QMouseEvent, QClipboard
from PyQt5.QtWidgets import QMainWindow, QWidget, QHBoxLayout, QPushButton, QMenu, QSizePolicy, QLayout, QFrame, \
    QSpacerItem

from src.filesystem.Folder import find_path, open_dir
from src.interface.commons.globals.CloseButton import CloseButton
from src.interface.commons.globals.TopFrame import TopFrame
from src.interface.external.ToolWindow import wOpen
from src.interface.external.Window import createSubWindow
from src.interface.external.filemanager.DirectoryPicker import DirectoryPicker
from src.interface.external.filemanager.FileCreator import FileCreator
from src.interface.external.filemanager.FilePicker import FilePicker
from src.interface.external.filemanager.FileSaver import FileSaver
from src.interface.external.html.Renderer import Renderer
from src.signals.Variables import DataBase as db


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
        layout.addWidget(ApplicationLabel(self, self.mw, self.___clipboard), 30)
        layout.addWidget(MinimizeButton(self, self.mw), 2)
        layout.addWidget(MaximizeButton(self, self.mw), 2)
        layout.addSpacerItem(QSpacerItem(1, 15, QSizePolicy.Fixed, QSizePolicy.Fixed))
        layout.addWidget(CloseButton.preset(self, "WINDOW"), 2)
        self.setLayout(layout)


class IconButton(QPushButton):
    def __init__(self, parent):
        super().__init__(parent)
        icon_size: QSize = QSize()
        size = 20
        icon_size.setHeight(size)
        icon_size.setWidth(size)
        icon = QIcon(find_path("Logo.png"))
        self.setIcon(icon)
        self.setIconSize(icon_size)
        self.setObjectName("Icon")
        self.setFixedSize(size+15, size+14)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
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
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Change Working Path", lambda: wOpen(self.parent().mw, DirectoryPicker(), "Setup Working Directory"))
        menu.addSeparator()
        menu.addAction("Open", lambda: wOpen(self.parent().mw, FilePicker(), "Open a File"))
        menu.addAction("New", lambda: wOpen(self.parent().mw, FileCreator(), "Create a New File"))
        menu.addAction("Save as...", lambda: wOpen(self.parent().mw, FileSaver(), "Save the current file as ..."))
        menu.addSeparator()
        menu.addAction("Options")
        self.setMenu(menu)


class HelpMenu(QPushButton):
    def __init__(self, parent):
        super(HelpMenu, self).__init__(parent)
        self.setText(" Help")
        self.setObjectName("Help")
        self.configure()
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Features", lambda: createSubWindow("Features", self, QWidget))
        menu.addSeparator()
        menu.addAction("8088 Instructions", lambda: createSubWindow("8088", self, Renderer, find_path("8088.md")))
        menu.addAction("IJVM Instructions", lambda: createSubWindow("IJVM", self, Renderer, find_path("IJVM.html")))
        self.setMenu(menu)


class MinimizeButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super().__init__(parent)
        self.mainwindow = mw
        self.setIcon(QIcon(find_path("minimize.png")))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Minimize")
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        self.mainwindow.showMinimized()


class MaximizeButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super().__init__(parent)
        self.mainwindow = mw
        self.setIcon(QIcon(find_path("maximize.png")))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Minimize")
        self.___event_enabled = True
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        if not self.mainwindow.isMaximized():
            self.mainwindow.showMaximized()
            self.setIcon(QIcon(find_path("restore.png")))
        else:
            self.mainwindow.showNormal()
            self.setIcon(QIcon(find_path("maximize.png")))


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

