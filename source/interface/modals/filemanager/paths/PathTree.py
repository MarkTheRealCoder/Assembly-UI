import os

from PyQt5.QtCore import QModelIndex, QTimer
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView, QTreeView, QSizePolicy

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import IconManager
from source.filesystem import find_path, get_available_disks, ls
from source.filesystem.documents import Document
from source.filesystem.documents import FT
from source.interface.assets import translateQSS
from source.interface.shared import Settings
from source.platform import isWindows


class Item(QStandardItem):

    def __init__(self, text: str, ext: str = ""):

        self.___is_file = False
        super().__init__(IconManager.getInstance().getIcon(ext), text)
        if ext == "":
            self.appendRow(QStandardItem("dummy"))
        else:
            self.___is_file = True

    def is_file(self):
        return self.___is_file


class PathTreeGraphic(QTreeView):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        with open(find_path("tree.qss")) as f:
            self.setStyleSheet(translateQSS(f.read()))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHeaderHidden(True)
        self.setAnimated(True)
        self.setModel(QStandardItemModel(self))

GET_CWD = lambda: Settings.getOrExcept("application/cwd", error_message="A Working Directory must be set in order to use this component in file mode!")

class PathTreeLogic(PathTreeGraphic):
    def __init__(self, parent, is_file: bool = False):
        super().__init__(parent)
        self.___exts = FT.SOURCE_EXTENSIONS if is_file else ()
        self.starting_point(is_file)

    def starting_point(self, is_file: bool):
        model: QStandardItemModel = self.model()
        items = []
        if not is_file:
            items += [(i, "") for i in get_available_disks()]
        else:
            items += ls(GET_CWD(), self.___exts)
        for i in items:
            item = Item(*i)
            model.appendRow(item)
            if item.hasChildren() and not is_file:
                indx = model.indexFromItem(item)
                self.expand(indx)
                self.add_subdirectories(indx)
        model.invisibleRootItem().setData(len(items))

    def update(self, item: Item = None):
        root = item is None
        is_file = self.___exts != ()
        starting_item = self.model().invisibleRootItem() if root else item
        items_num = starting_item.data()
        if root and items_num == 0:
            self.starting_point(is_file)
            return

        items = []
        if root:
            if is_file:
                items += ls(GET_CWD(), self.___exts)
            else:
                items += [(i, "") for i in get_available_disks()]
        else:
            items += ls(self.genPathFromItem(starting_item), self.___exts)

        items = {n: e for n, e in items}

        num = starting_item.rowCount()
        i = 0
        while i < num:
            it = starting_item.child(i)
            if it is None:
                i += 1
                continue
            item_text = it.text()
            extension = items.get(item_text)
            if extension is None or not isinstance(it, Item) or it.is_file() != bool(extension):
                starting_item.removeRow(i)
                num -= 1
                continue
            items.pop(item_text)
            if self.isExpanded(it.index()):
                self.update(it)
            i += 1
        for n, e in items.items():
            starting_item.appendRow(Item(n, e))
        starting_item.setData(starting_item.rowCount())

    def get_path(self, index: QModelIndex) -> tuple[str, bool]:
        item: Item = self.model().itemFromIndex(index)
        path: str = self.genPathFromItem(item)
        return path, item.is_file()

    def add_subdirectories(self, index: QModelIndex):
        if not index.isValid():
            return
        model: QStandardItemModel = self.model()
        item: Item = model.itemFromIndex(index)
        dummy = item.child(0, 0)
        if dummy is not None and not isinstance(dummy, Item):
            item_names = ls(self.genPathFromItem(item), self.___exts)
            items = [Item(*i) for i in item_names]
            if items:
                item.appendRows(items)
            item.setData(len(items))
            item.removeRow(0)

    def genPathFromItem(self, item: Item):
        parts: list[str] = []
        copy = item
        while copy is not None:
            parts.append(copy.text())
            copy = copy.parent()
        parts.reverse()

        if self.___exts == ():
            joined = Document.SEP.join(parts) if isWindows() else os.path.join(*parts)
            path = os.path.normpath(joined)
            if not item.is_file() and not path.endswith(Document.SEP):
                path += Document.SEP
            return path

        base = GET_CWD()
        joined = Document.SEP.join(parts)
        return os.path.normpath(os.path.join(base, joined.lstrip(Document.SEP))) + (
            Document.SEP if not item.is_file() else ""
        )


@EventRegister.register(ClosingEvent, "Tool", EventRegister.URGENT)
class PathTree(PathTreeLogic):
    def __init__(self, parent, is_file: bool = False):
        super().__init__(parent, is_file)

        self.___timer = QTimer(self)
        self.___timer.timeout.connect(self.update)
        self.___timer.start(1000)
        self.___placeholder_dc: callable = lambda x, y: None # double click
        self.___placeholder_c: callable = lambda x, y: None # click

        self.expanded.connect(self.add_subdirectories)
        self.doubleClicked.connect(lambda x: self.___placeholder_dc(*self.get_path(x))) # double click
        self.clicked.connect(lambda x: self.___placeholder_c(*self.get_path(x))) # click

    def onClosingEvent(self, event):
        self.___timer.stop()

    def onDoubleClick(self, func: callable):
        if not callable(func):
            raise TypeError("A callable was expected...")
        self.___placeholder_dc = func

    def onClick(self, func: callable):
        if not callable(func):
            raise TypeError("A callable was expected...")
        self.___placeholder_c = func

    def event(self, event):
        return super().event(event)



