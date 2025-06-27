from PyQt5.QtGui import QIcon

from source.filesystem.Folder import find_path
from source.interface.modals.filemanager.complex.buttons.Button import Button


class ConfirmButton(Button):
    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(QIcon(find_path("confirm.png")))
        self.setToolTip("Confirm choices")

