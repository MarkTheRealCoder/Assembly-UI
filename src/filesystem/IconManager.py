from typing import Union

from PyQt5.QtGui import QIcon

from src.filesystem.Folder import find_path
from src.filesystem.documents.FileTypes import FT, Filetypes


class IconManager:
    _icon_manager = None

    def __init__(self):
        self.___icons = {
            FT.FFOLD: QIcon(find_path("directories.png")),
            FT.FIJVM: QIcon(find_path("ijvm_icon.png")),
            FT.F8088: QIcon(find_path("a8088_icona.png"))
        }

    def getIcon(self, ext: Union[str, int, Filetypes]) -> QIcon:
        prompt: Filetypes = None
        if isinstance(ext, str):
            prompt = FT.findByExt(ext)
        elif isinstance(ext, Filetypes):
            prompt = ext
        else:
            prompt = FT.findById(ext)
        return self.___icons.get(prompt, self.___icons.get(FT.FFOLD))

    @staticmethod
    def getInstance():
        if IconManager._icon_manager is None:
            IconManager._icon_manager = IconManager()
        return IconManager._icon_manager
