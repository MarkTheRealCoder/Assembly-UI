from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView, QTreeView, QSizePolicy

from source.asyncro.Scheduler import Scheduler
from source.comms.Signals import DataBase as db
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import IconManager
from source.filesystem.Folder import find_path, get_available_disks, ls
from source.filesystem.documents.Document import Document
from source.filesystem.documents.FileTypes import FT
from source.interface.assets import translateQSS
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


class PathTreeLogic(PathTreeGraphic):
    def __init__(self, parent, is_file: bool = False):
        super().__init__(parent)
        self.___exts = () if not is_file else (str(FT.FIJVM), str(FT.F8088))
        self.starting_point(is_file)

    def starting_point(self, is_file: bool):
        model: QStandardItemModel = self.model()
        items = []
        if not is_file:
            items += [(i, "") for i in get_available_disks()]
        else:
            items += ls(db.FOLDER.getValue(), self.___exts)
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
                items += ls(db.FOLDER.getValue(), self.___exts)
            else:
                items += [(i, "") for i in get_available_disks()]
        else:
            items += ls(self.genPathFromItem(starting_item), self.___exts)

        items = {n: e for n, e in items}

        num = items_num
        for i in range(num):
            it = starting_item.child(i)
            item_text = it.text()
            v = items.pop(item_text, None)
            if v is None:
                starting_item.removeRow(i)
                items_num -= 1
            elif self.isExpanded(it.index()):
                self.update(it)  # noqas
        for n, e in items.items():
            starting_item.appendRow(Item(n, e))
            items_num += 1
        starting_item.setData(items_num)

    def get_path(self, index: QModelIndex) -> tuple[str, bool]:
        item: Item = self.model().itemFromIndex(index)
        path: str = self.genPathFromItem(item)
        is_file = self.___exts != () and ("." in item.text())
        return path, is_file

    def add_subdirectories(self, index: QModelIndex):
        if not index.isValid():
            return
        model: QStandardItemModel = self.model()
        item: Item = model.itemFromIndex(index)
        dummy = item.child(0, 0)
        if dummy.text() == "dummy":
            item_names = ls(self.genPathFromItem(item), self.___exts)
            items = [Item(*i) for i in item_names]
            if items:
                item.appendRows(items)
            item.setData(len(items))
            item.removeRow(0)

    def genPathFromItem(self, item: Item):
        result = ""
        copy = item
        items: list[str] = [copy.text()]
        while copy.parent() is not None:
            parent = copy.parent()
            items.append(parent.text())
            copy = parent
        if self.___exts == ():
            if not isWindows():
                items[-1] = ""  # For fixing main directory issue
        else:
            result += db.FOLDER.getValue()
        return result + Document.SEP.join(items[::-1]) + (Document.SEP if not item.is_file() else "")


@EventRegister.register(ClosingEvent, "Tool", EventRegister.URGENT)
class PathTree(PathTreeLogic):
    def __init__(self, parent, is_file: bool = False):
        super().__init__(parent, is_file)

        self.___scheduler: Scheduler = Scheduler(1, self.update)
        self.___placeholder_dc: callable = lambda x, y: None # double click
        self.___placeholder_c: callable = lambda x, y: None # click

        self.expanded.connect(self.add_subdirectories)
        self.doubleClicked.connect(lambda x: self.___placeholder_dc(*self.get_path(x))) # double click
        self.clicked.connect(lambda x: self.___placeholder_c(*self.get_path(x))) # click

    def onClosingEvent(self, event):
        self.___scheduler.terminate()

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



