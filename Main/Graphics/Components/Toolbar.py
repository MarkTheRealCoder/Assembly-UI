import os

from PyQt5.QtCore import QSize, Qt, QPoint, QEvent, QObject, QRect, QModelIndex
from PyQt5.QtGui import QIcon, QMouseEvent, QStandardItem, QStandardItemModel, QClipboard
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWidget, QLabel, QHBoxLayout, QPushButton, QMenu, QDesktopWidget, \
    QVBoxLayout, QAbstractItemView, QTreeView, QSizePolicy

from Main.Tools.Tools import find_path as find_icon, find_path, ls, HandleJson
from Main.Tools.Tools import openDir, Variable

LABEL: Variable = Variable(os.getcwd())
OPEN_FILE: Variable("")


class ToolBar(QWidget):

    trashWindow: QMainWindow = None

    def __init__(self, mwt: QWidget, app: QClipboard):
        super(QWidget, self).__init__()
        self.setParent(mwt)
        self.clipboard: QClipboard = app
        # noinspection PyTypeChecker
        self.mw: QMainWindow = mwt.parent()
        self.size: QSize = self.mw.size()
        self.size.setHeight(30)
        self.setFixedSize(self.size)
        self.addComponents()
        self.setObjectName("Toolbar")
        self.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

    def addComponents(self):
        layout = QHBoxLayout()
        layout.addWidget(self.add_icon_button(), 0, Qt.AlignLeft)
        layout.addWidget(self.add_file_menu(), 0, Qt.AlignLeft)
        layout.addWidget(self.add_help_menu(), 0, Qt.AlignLeft)
        layout.addWidget(self.add_run_button(), 0, Qt.AlignLeft)
        layout.addWidget(self.add_text_label(), 0, Qt.AlignLeft)
        layout.addWidget(self.add_mode_button(), 0, Qt.AlignLeft)
        layout.addWidget(self.add_minimize_button(), 0, Qt.AlignLeft)
        layout.addWidget(self.add_close_button(), 0, Qt.AlignLeft)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def add_icon_button(self):
        return IconButton(self)

    def add_file_menu(self):
        file = FileMenu(self)
        menu = QMenu()
        menu.addAction("Change Working Path", lambda: self.wOpen(anywidget=DisplayPath()))
        menu.addSeparator()
        menu.addAction("Open", lambda: self.wOpen(anywidget=DisplayPath(path=LABEL.getContent(), ext=("ijvm", "8088"))))
        menu.addAction("New")
        menu.addSeparator()
        menu.addAction("Save as...")
        menu.setObjectName("MenuFile")
        menu.setStyleSheet("""
                QMenu#MenuFile {
                    background-color: #1E1E1E;
                    color: #E48300;
                }

                QMenu#MenuFile::item:selected {
                    color: #00AAFF;
                }
            """)
        file.setMenu(menu)
        return file

    def add_run_button(self):
        return RunButton(self)

    def add_help_menu(self):
        help = HelpMenu(self)
        menu = QMenu()
        menu.addAction("Features")
        menu.addSeparator()
        menu.addAction("8088 Instructions")
        menu.addAction("IJVM Instructions")
        menu.setObjectName("MenuHelp")
        help.setContextMenuPolicy(Qt.CustomContextMenu)
        menu.setStyleSheet("""
                            QMenu#MenuHelp {
                                background-color: #1E1E1E;
                                color: #E48300;
                            }

                            QMenu#MenuHelp::item:selected {
                                color: #00AAFF;
                            }
                        """)
        help.setMenu(menu)
        return help

    def add_text_label(self):
        return ApplicationLabel(self, self.mw, self.clipboard)

    def add_mode_button(self):
        return UserModeButton(self)

    def add_minimize_button(self):
        return MinimizeButton(self, self.mw)

    def add_close_button(self):
        return CloseButton(self, self.mw)

    @staticmethod
    def wOpen(anywidget=None, size: tuple = (400, 450)):
        ToolBar.trashWindow = TrashWindow(anywidget, size)
        ToolBar.trashWindow.show()


class IconButton(QPushButton):
    def __init__(self, parent):
        super(IconButton, self).__init__(None)
        self.setParent(parent)
        self.setFixedWidth(30)
        self.setFixedHeight(parent.height())
        iconSize: QSize = QSize()
        iconSize.setHeight(20)
        iconSize.setWidth(20)
        icon = QIcon(find_icon("Logo.png"))
        self.setIcon(icon)
        self.setIconSize(iconSize)
        self.setObjectName("Icon")


class FileMenu(QPushButton):
    def __init__(self, parent):
        super(FileMenu, self).__init__(None)
        self.setParent(parent)
        self.setFixedWidth(50)
        self.setFixedHeight(parent.height())
        self.setText("File")
        self.setObjectName("File")


class RunButton(QPushButton):
    def __init__(self, parent):
        super(RunButton, self).__init__(None)
        self.setParent(parent)
        self.setFixedWidth(50)
        self.setFixedHeight(parent.height())
        self.setText("▶")
        self.setObjectName("Run")


class HelpMenu(QPushButton):
    def __init__(self, parent):
        super(HelpMenu, self).__init__(None)
        self.setParent(parent)
        self.setFixedWidth(50)
        self.setFixedHeight(parent.height())
        self.setText("Help")
        self.setObjectName("Help")


class ApplicationLabel(QLabel):

    handlejson: HandleJson = HandleJson()
    movable: bool = False

    def __init__(self, parent, mw: QMainWindow, clip: QClipboard):
        super(ApplicationLabel, self).__init__()
        self.clipboard = clip

        global LABEL
        LABEL.change_content.connect(self.setLabel)

        self.currentDirectory: str = ApplicationLabel.handlejson.get("cwd")
        if self.currentDirectory is None:
            LABEL.setContent(os.getcwd())
        else:
            LABEL.setContent(self.currentDirectory)

        self.label = f"Assembly Stdio - {self.currentDirectory}"
        self.mw: QMainWindow = mw
        self.__mousePressPos = 0
        self.__mouseMovePos = 0
        self.setParent(parent)
        self.setFixedWidth(620)
        self.setFixedHeight(parent.height())
        self.setText(self.label)
        self.setObjectName("Title")
        self.setAlignment(Qt.AlignCenter)
        self.installEventFilter(self)

    def setLabel(self):
        global LABEL
        self.currentDirectory = LABEL.getContent()
        self.setText(f"Assembly Stdio - {self.currentDirectory}")
        ApplicationLabel.handlejson.encodeAndSave("cwd", self.currentDirectory)

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.MouseButtonDblClick and e.button() == Qt.LeftButton:
            self.clipboard.setText(self.currentDirectory, mode=self.clipboard.Clipboard)
        elif e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton and e.modifiers() & Qt.ControlModifier:
            openDir(self.currentDirectory)
        elif e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
            ApplicationLabel.movable = True
            self.__mousePressPos = e.globalPos()
            self.__mouseMovePos = e.globalPos()
        elif e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
            ApplicationLabel.movable = False
        elif e.type() == QEvent.MouseMove and ApplicationLabel.movable:
            self.moveWindow(e)
        return super().eventFilter(o, e)

    def moveWindow(self, e: QEvent):
        desk = QDesktopWidget()
        screen_rect: QRect = desk.availableGeometry()
        del desk
        bottom_right: QPoint = screen_rect.bottomRight()
        globalPos = e.globalPos()
        diff = globalPos - self.__mouseMovePos
        self.__mouseMovePos = globalPos
        curr_pos: QPoint = self.mw.pos()
        if (curr_pos.y() + diff.y()) < bottom_right.y() - 15:
            self.mw.move(curr_pos + diff)


class UserModeButton(QPushButton):

    mode: bool = False
    color: dict = {
        False: "background-color: #10E830;",
        True: "background-color: #E81010;"
    }

    def __init__(self, parent):
        super(UserModeButton, self).__init__()
        self.setParent(parent)
        self.setFixedWidth(340)
        self.setFixedHeight(parent.height())
        iconSize: QSize = QSize()
        iconSize.setHeight(29)
        iconSize.setWidth(340)
        icon = QIcon(find_icon("mode.png"))
        self.setIcon(icon)
        self.setIconSize(iconSize)
        self.setObjectName("Mode")
        self.installEventFilter(self)

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
            UserModeButton.mode = not UserModeButton.mode
            self.setStyleSheet(UserModeButton.color.get(UserModeButton.mode))
        return super().eventFilter(o, e)


class MinimizeButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super(MinimizeButton, self).__init__(None)
        self.mainwindow = mw
        self.setParent(parent)
        self.setFixedWidth(30)
        self.setFixedHeight(parent.height())
        self.setText("_")
        self.setObjectName("Minimize")

    def mousePressEvent(self, e: QMouseEvent):
        self.mainwindow.showMinimized()


class CloseButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super(CloseButton, self).__init__(None)
        self.mainwindow = mw
        self.setParent(parent)
        self.setFixedWidth(30)
        self.setFixedHeight(parent.height())
        self.setText("x")
        self.setObjectName("Close")

    def mousePressEvent(self, e: QMouseEvent):
        self.mainwindow.close()


class TrashWindow(QMainWindow):

    def __init__(self, widget=None, size: tuple = (300, 300)):
        super(QMainWindow, self).__init__()
        self.setObjectName("Trash")
        self.setConfigurations(size)

        self.widget: QWidget = QWidget(self)
        self.widget.setAutoFillBackground(True)

        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        layout.addWidget(self.topBorder(), 0, Qt.AlignTop | Qt.AlignLeft)

        if widget is not None:
            widget.setSize(self)
            widget.setParent(self.widget)
            layout.addWidget(widget, 0, Qt.AlignTop | Qt.AlignLeft)

        self.setCentralWidget(self.widget)

    def setConfigurations(self, size: tuple):
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)
        self.setMinimumWidth(size[0])
        self.setMinimumHeight(size[1])
        with open(find_path("trash.qss"), "r") as f:
            self.setStyleSheet(f.read())
        self.centerOnScreen()

    def topBorder(self):
        widget: QWidget = QWidget(self.widget)
        widget.setFixedHeight(31)
        widget.setFixedWidth(self.width())
        layout: QHBoxLayout = QHBoxLayout(widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(TrashLabel(widget, self), 0, Qt.AlignLeft | Qt.AlignTop)
        layout.addWidget(TrashButton(widget, self), 0, Qt.AlignLeft | Qt.AlignTop)
        widget.setLayout(layout)
        return widget

    def centerOnScreen(self):
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        x = (screen_geometry.width() - self.width()) / 2
        y = (screen_geometry.height() - self.height()) / 2
        self.move(x, y)


class TrashLabel(QLabel):

    movable: bool = False

    def __init__(self, parent, mw: QMainWindow):
        super(QLabel, self).__init__(parent)
        self.mw: QMainWindow = mw
        self.setFixedHeight(31)
        self.setFixedWidth(mw.width() - 40)
        self.setObjectName("Label")
        self.__mousePressPos = 0
        self.__mouseMovePos = 0
        self.installEventFilter(self)

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if e.type() == QEvent.MouseButtonPress and e.button() == Qt.LeftButton:
            TrashLabel.movable = True
            self.__mousePressPos = e.globalPos()
            self.__mouseMovePos = e.globalPos()
        elif e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
            TrashLabel.movable = False
        elif e.type() == QEvent.MouseMove and TrashLabel.movable:
            self.moveWindow(e)
        return super().eventFilter(o, e)

    def moveWindow(self, e: QEvent):
        desk = QDesktopWidget()
        screen_rect: QRect = desk.availableGeometry()
        del desk
        bottom_right: QPoint = screen_rect.bottomRight()
        globalPos = e.globalPos()
        diff = globalPos - self.__mouseMovePos
        self.__mouseMovePos = globalPos
        curr_pos: QPoint = self.mw.pos()
        if (curr_pos.y() + diff.y()) < bottom_right.y() - 15:
            self.mw.move(curr_pos + diff)


class TrashButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super(QPushButton, self).__init__(parent)
        self.mw: QMainWindow = mw
        self.setFixedHeight(31)
        self.setFixedWidth(40)
        self.setText("x")
        self.setObjectName("Button")

    def mousePressEvent(self, e: QEvent):
        self.mw.close()


class DisplayPath(QTreeView):

    root = "C:\\" if os.name == "nt" else "/"
    sep = "\\" if os.name == "nt" else "/"

    def __init__(self, parent=None, path: str = root, ext: tuple = ()):
        super(QTreeView, self).__init__(parent=parent)
        DisplayPath.root = path
        self.path = path
        self.ext = ext
        with open(find_path("tree.qss")) as f:
            self.setStyleSheet(f.read())
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.dirsIcon = self.setIconForDirs()

        self.model = QStandardItemModel()

        self.setHeaderHidden(True)

        self.firstItem = QStandardItem(path)
        self.model.appendRow(self.firstItem)
        self.editModel(self.firstItem)

        self.setModel(self.model)
        self.expand(self.firstItem.index())

        self.expanded.connect(lambda index: self.addElements(index))
        self.doubleClicked.connect(lambda index: self.setPath(index))

    def setSize(self, parentWindow):
        self.setMinimumWidth(parentWindow.width())
        self.setMinimumHeight(parentWindow.height() - 31)

    @staticmethod
    def setIconForDirs():
        return QIcon(find_path("directories.png"))

    def editModel(self, parent: QStandardItem):
        if parent.hasChildren():
            if parent.child(0).text() != "expandible":
                return
            parent.removeRow(0)

        elements = ls(self.path, self.ext)

        if elements is None:
            return

        files: dict[str: bool] = elements[1]

        for i in files.items():
            item = QStandardItem(i[0])
            item.setIcon(self.dirsIcon)
            if i[1]:
                item.appendRow(QStandardItem("expandible"))
            parent.appendRow(item)

    def setCurrPath(self, item):
        tmp = item.text()
        if tmp == DisplayPath.root:
            self.path = DisplayPath.root
            return
        tmp += DisplayPath.sep
        parent = item.parent()
        while True:
            tmp2 = parent.text()
            if tmp2 == DisplayPath.root:
                tmp = tmp2 + tmp
                break
            else:
                tmp = tmp2 + DisplayPath.sep + tmp
            parent = parent.parent()
        self.path = tmp

    def addElements(self, index: QModelIndex):
        item = self.model.itemFromIndex(index)
        self.setCurrPath(item)
        self.editModel(item)

    def setPath(self, index: QModelIndex):
        item = self.model.itemFromIndex(index)
        if self.ext != ():
            if not any([item.text().endswith(i) for i in self.ext]):
                return
        self.setCurrPath(item)
        if self.ext == ():
            global LABEL
            LABEL.setContent(self.path[0:len(self.path) - 1])
        else:
            global OPEN_FILE
            OPEN_FILE.setContent(self.path[0:len(self.path) - 1])
        self.parent().parent().close()
