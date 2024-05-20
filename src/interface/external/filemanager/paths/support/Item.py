from PyQt5.QtGui import QStandardItem

from src.filesystem.IconManager import IconManager


class PathItem(QStandardItem):

    def __init__(self, text: str, ext: str = ""):

        self.___is_file = False
        super().__init__(IconManager.getInstance().getIcon(ext), text)
        if ext == "":
            self.appendRow(QStandardItem("dummy"))
        else:
            self.___is_file = True

    def is_file(self):
        return self.___is_file


