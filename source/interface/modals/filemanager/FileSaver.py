from pathlib import Path
import os

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import resolve_app_path
from source.filesystem.documents import Document, FT
from source.interface.modals.filemanager.complex import FileDialog
from source.interface.shared import Settings


class FileSaver(FileDialog):
    def __new__(cls, *args, **kwargs):
        if Settings.get("editor/current", None):
            return super().__new__(cls)
        return None

    def __init__(self):
        if path := Settings.get("editor/current", None):
            self.cd: Document = Document(path)
            exts = ["ijvm", "jas"]
            if FT.findByExt(self.cd.getExtension()) == 2:
                exts = ["a8088", "asm"]
            super().__init__(exts, name=self.cd.getName())
            self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        path = resolve_app_path(self.get_path())
        ext = self.get_extension().lower()

        if name == "":
            return

        full_path = os.path.join(path, f"{name}.{ext}")

        file = Path(full_path)
        try:
            file.touch()
        except FileExistsError:
            pass

        with open(full_path, "w", newline="\n") as file:
            file.write(self.cd.text)

        EventRegister.send(ClosingEvent(), "Tool")




