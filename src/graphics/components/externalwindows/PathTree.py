from PyQt5.QtCore import QModelIndex
from PyQt5.QtGui import QStandardItemModel, QStandardItem
from PyQt5.QtWidgets import QAbstractItemView, QTreeView, QSizePolicy

from src.graphics.components.externalwindows.pathtreesupport.Item import ItemFactory
from src.tools.Tools import find_path, get_available_disks, ls, isWindows
from src.tools.Variables import DataBase as db
from src.tools.documents.Document import Document
from src.tools.documents.FileTypes import FT


class PathTree(QTreeView):
    def __init__(self, parent, is_file: bool = False):
        super().__init__(parent)
        self.paths: list[list[str]] = []

        self.configurations(is_file)

        self.starting_point(is_file)

        self.expanded.connect(self.add_subdirectories)
        self.destroyed.connect(self.emergency)
        #self.doubleClicked.connect(lambda index: self.setPath(index))
        self.setAnimated(True)

    def configurations(self, is_file: bool):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        with open(find_path("tree.qss")) as f:
            self.setStyleSheet(f.read())
        self.setEditTriggers(QAbstractItemView.NoEditTriggers)
        self.setHeaderHidden(True)
        model = QStandardItemModel(self)
        self.setModel(model)

    def starting_point(self, is_file: bool):
        model: QStandardItemModel = self.model()
        items = []
        if not is_file:
            items += [ItemFactory.item(i, FT.FFOLD) for i in get_available_disks()]
        else:
            items.append(ItemFactory.item(db.FOLDER.getValue(), FT.FFOLD))
        model.appendColumn(items)

    def add_subdirectories(self, index: QModelIndex):
        if not index.isValid():
            return
        model: QStandardItemModel = self.model()
        item: QStandardItem = model.itemFromIndex(index)
        dummy = item.child(0, 0)
        if dummy.text() == "dummy":
            item_names = ls(self.genPathFromItem(item))
            items = [ItemFactory.item(i, FT.FFOLD) for i in item_names]
            if items:
                print("DONE")
                item.appendRows(items)
                print("COMPLETED")
            item.removeRow(0)

    def genPathFromItem(self, item: QStandardItem):
        copy = item
        items: list[str] = [copy.text()]
        while copy.parent() is not None:
            parent = copy.parent()
            items.append(parent.text())
            copy = parent
        if not isWindows():
            items[-1] = ""  # For fixing main directory issue
        return Document.SEP.join(items[::-1]) + Document.SEP

    def emergency(self, o):
        self.expanded.disconnect()
        self.destroyed.disconnect()
        self.model().clear()

    # Event handling

