from PyQt5.QtGui import QIcon

from src.filesystem.Folder import find_path
from src.interface.external.filemanager.complex.buttons.Button import Button


class HomeButton(Button):
    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(QIcon(find_path("home.png")))
        self.setToolTip("Set current path to home")
