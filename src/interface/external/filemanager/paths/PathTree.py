from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel
from PyQt5.QtWidgets import QAbstractItemView, QTreeView, QSizePolicy

from src.asynctasks.Scheduler import Scheduler
from src.eventhandlers.Register import EventRegister
from src.events.data.ClosingEvent import ClosingEvent
from src.filesystem.Folder import find_path, get_available_disks, ls
from src.filesystem.documents.Document import Document
from src.filesystem.documents.FileTypes import FT
from src.interface.external.filemanager.paths.support.Item import PathItem
from src.platform.Adaptability import translateQSS, isWindows
from src.signals.Variables import DataBase as db


@EventRegister.register(ClosingEvent, "Tool", EventRegister.URGENT)
class PathTree(QTreeView):
    def __init__(self, parent, is_file: bool = False):
        super().__init__(parent)
        self.___exts = () if not is_file else (str(FT.FIJVM), str(FT.F8088))

        self.configurations()

        self.starting_point(is_file)

        self.___scheduler: Scheduler = Scheduler(1, self.___update)
        self.___placeholder_dc: callable = lambda x, y: None
        self.___placeholder_c: callable = lambda x, y: None

        self.expanded.connect(self.add_subdirectories)
        self.doubleClicked.connect(lambda x: self.___placeholder_dc(*self.get_path(x)))
        self.clicked.connect(lambda x: self.___placeholder_c(*self.get_path(x)))

    def onClosingEvent(self, event):
        self.___scheduler.terminate()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        with open(find_path("tree.qss")) as f:
            self.setStyleSheet(translateQSS(f.read()))
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHeaderHidden(True)
        self.setAnimated(True)
        model = QStandardItemModel(self)
        self.setModel(model)

    def starting_point(self, is_file: bool):
        model: QStandardItemModel = self.model()
        items = []
        if not is_file:
            items += [(i, "") for i in get_available_disks()]
        else:
            items += ls(db.FOLDER.getValue(), self.___exts)
        for i in items:
            item = PathItem(*i)
            model.appendRow(item)
            if item.hasChildren() and not is_file:
                indx = model.indexFromItem(item)
                self.expand(indx)
                self.add_subdirectories(indx)
        model.invisibleRootItem().setData(len(items))

    def add_subdirectories(self, index: QModelIndex):
        if not index.isValid():
            return
        model: QStandardItemModel = self.model()
        item: PathItem = model.itemFromIndex(index)
        dummy = item.child(0, 0)
        if dummy.text() == "dummy":
            item_names = ls(self.genPathFromItem(item), self.___exts)
            items = [PathItem(*i) for i in item_names]
            if items:
                item.appendRows(items)
            item.setData(len(items))
            item.removeRow(0)

    def genPathFromItem(self, item: PathItem):
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

    def get_path(self, index: QModelIndex) -> tuple[str, bool]:
        item: PathItem = self.model().itemFromIndex(index)
        path: str = self.genPathFromItem(item)
        is_file = self.___exts != () and ("." in item.text())
        return path, is_file

    def onDoubleClick(self, func: callable):
        if not callable(func):
            raise TypeError("A callable was expected...")
        self.___placeholder_dc = func

    def onClick(self, func: callable):
        if not callable(func):
            raise TypeError("A callable was expected...")
        self.___placeholder_c = func

    def ___update(self, item: PathItem = None):
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
                self.___update(it)  # noqas
        for n, e in items.items():
            starting_item.appendRow(PathItem(n, e))
            items_num += 1
        starting_item.setData(items_num)








