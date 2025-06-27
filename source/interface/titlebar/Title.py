from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QApplication

from source.comms.Signals import DataBase as db
from source.filesystem import open_dir
from source.interface.templates import Title


class Title(Title):
    def __init__(self, parent, mw: QMainWindow):
        super().__init__(parent, mw)
        db.FOLDER.connect(self.setLabel)
        self.setAlignment(Qt.AlignCenter)

        self.___curr_dir = None

        self.setLabel()

        self.setActionOn("LeftDoubleClick", lambda: QApplication.clipboard().setText(self.___curr_dir, mode=QApplication.clipboard().Clipboard))
        self.setActionOn("LeftCtrlClick", lambda: open_dir(self.___curr_dir))

    def setLabel(self):
        self.___curr_dir = db.FOLDER.getValue()
        self.setText(f"Assembly Stdio - {self.___curr_dir}")