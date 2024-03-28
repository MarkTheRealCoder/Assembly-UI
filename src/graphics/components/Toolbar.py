from PyQt5.QtCore import QSize, Qt, QPoint, QEvent, QObject, QRect
from PyQt5.QtGui import QIcon, QMouseEvent, QClipboard
from PyQt5.QtWidgets import QMainWindow, QWidget, QLabel, QHBoxLayout, QPushButton, QMenu, QDesktopWidget, \
    QSizePolicy, QLayout, QFrame, QSpacerItem

from src.graphics.components.externalwindows.PathTree import PathTree
from src.graphics.components.trashcomponents.TrashWindow import wOpen
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
        layout.addWidget(self.add_icon_button(), 0)
        layout.addWidget(self.add_file_menu(), 2)
        layout.addWidget(self.add_help_menu(), 2)
        layout.addWidget(self.add_run_button(), 2)
        layout.addWidget(self.add_text_label(), 30)
        layout.addWidget(self.add_minimize_button(), 2)
        layout.addSpacerItem(QSpacerItem(1, 15, QSizePolicy.Fixed, QSizePolicy.Fixed))
        layout.addWidget(self.add_close_button(), 2)
        self.setLayout(layout)

    def add_icon_button(self):
        btn = IconButton(self)
        btn.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        return btn

    def add_file_menu(self):
        file = FileMenu(self)
        file.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        return file

    def add_help_menu(self):
        _help = HelpMenu(self)
        _help.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        return _help

    def add_run_button(self):
        btn = RunButton(self)
        btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        return btn

    def add_text_label(self):
        label = ApplicationLabel(self, self.mw, self.___clipboard)
        label.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        return label

    def add_minimize_button(self):
        btn = MinimizeButton(self, self.mw)
        btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        return btn

    def add_close_button(self):
        btn = CloseButton(self, self.mw)
        btn.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)
        return btn


class IconButton(QPushButton):
    def __init__(self, parent):
        super(IconButton, self).__init__(None)
        self.setParent(parent)
        icon_size: QSize = QSize()
        size = 20
        icon_size.setHeight(size)
        icon_size.setWidth(size)
        icon = QIcon(find_icon("Logo.png"))
        self.setIcon(icon)
        self.setIconSize(icon_size)
        self.setObjectName("Icon")
        self.setFixedSize(size+15, size+14)
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

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)

    def configure(self):
        menu = QMenu(self)
        menu.addAction("Change Working Path", lambda: wOpen(anywidget=PathTree(None)))
        menu.addSeparator()
        menu.addAction("Open", lambda: wOpen(anywidget=PathTree(None, True)))
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

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        super().mousePressEvent(e)


class ApplicationLabel(QLabel):
    movable: bool = False

    def __init__(self, parent, mw: QMainWindow, clip: QClipboard):
        super(ApplicationLabel, self).__init__()
        self.clipboard = clip

        db.FOLDER.connect(self.setLabel)

        self.label = f"Assembly Stdio - {db.FOLDER.getValue()}"
        self.mw: QMainWindow = mw
        self.__mousePressPos = 0
        self.__mouseMovePos = 0
        self.setParent(parent)
        self.setText(self.label)
        self.setObjectName("Title")
        self.setAlignment(Qt.AlignCenter)
        self.setSizePolicy(QSizePolicy.Maximum, QSizePolicy.Fixed)

        self.installEventFilter(self)
        self.___event_enabled = True

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def setLabel(self):
        self.currentDirectory = db.FOLDER.getValue()
        self.setText(f"Assembly Stdio - {self.currentDirectory}")

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if not self.___event_enabled:
            return super().eventFilter(o, e)

        if e.type() == QEvent.MouseMove and ApplicationLabel.movable:
            self.moveWindow(e)

        elif hasattr(e, "button") and e.button() == Qt.LeftButton:

            if e.type() == QEvent.MouseButtonDblClick:
                self.clipboard.setText(self.currentDirectory, mode=self.clipboard.Clipboard)

            elif e.type() == QEvent.MouseButtonPress:

                if e.modifiers() & Qt.ControlModifier:
                    open_dir(self.currentDirectory)
                else:
                    ApplicationLabel.movable = True  # e.pos().y() > 10
                    self.__mousePressPos = e.globalPos()
                    self.__mouseMovePos = e.globalPos()

            elif e.type() == QEvent.MouseButtonRelease:
                ApplicationLabel.movable = False

        return super().eventFilter(o, e)

    def moveWindow(self, e: QEvent):
        desk = QDesktopWidget()
        screen_rect: QRect = desk.availableGeometry()
        del desk
        bottom_right: QPoint = screen_rect.bottomRight()
        global_pos = e.globalPos()
        diff = global_pos - self.__mouseMovePos
        self.__mouseMovePos = global_pos
        curr_pos: QPoint = self.mw.pos()
        if (curr_pos.y() + diff.y()) < bottom_right.y() - 15:
            self.mw.move(curr_pos + diff)


class MinimizeButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super(MinimizeButton, self).__init__(None)
        self.mainwindow = mw
        self.setParent(parent)
        self.setText("_")
        self.setObjectName("Minimize")
        self.___event_enabled = True

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        self.mainwindow.showMinimized()


class CloseButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super(CloseButton, self).__init__(None)
        self.mainwindow = mw
        self.setParent(parent)
        self.setText("x")
        self.setObjectName("Close")
        self.___event_enabled = True

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        self.mainwindow.destroy(True, True)
        self.mainwindow.close()
