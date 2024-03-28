from PyQt5.QtGui import QStandardItem, QIcon

from src.tools.Tools import find_path
from src.tools.documents.FileTypes import Filetypes, FT


class ItemFactory:
    fts = None

    @staticmethod
    def item(text: str, ft: Filetypes):
        if ItemFactory.fts is None:
            ItemFactory.fts = {
                FT.FFOLD: QIcon(find_path("directories.png")),
                FT.FIJVM: QIcon(find_path("directories.png")),
                FT.F8088: QIcon(find_path("directories.png"))
            }
        item = QStandardItem(ItemFactory.fts.get(ft), text)
        item.appendRow(QStandardItem("dummy"))
        return item


