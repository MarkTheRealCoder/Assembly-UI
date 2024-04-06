from PyQt5.QtGui import QStandardItem, QIcon

from src.tools.Tools import find_path
from src.tools.documents.FileTypes import Filetypes, FT


class PathItem(QStandardItem):
    fts = None

    def __init__(self, text: str, ext: str = ""):
        if PathItem.fts is None:
            PathItem.fts = {
                FT.FFOLD: QIcon(find_path("directories.png")),
                FT.FIJVM: QIcon(find_path("directories.png")),
                FT.F8088: QIcon(find_path("directories.png"))
            }

        self.___is_file = False
        super().__init__(PathItem.fts.get(FT.findByExt(ext)), text)
        if ext == "":
            self.appendRow(QStandardItem("dummy"))
        else:
            self.___is_file = True

    def is_file(self):
        return self.___is_file


