from pathlib import Path

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem.documents import Document
from source.filesystem.documents import FT
from source.interface.modals.filemanager.complex import FileDialog
from source.interface.shared import Settings


class FileSaver(FileDialog):
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
        path = Settings.get("application/cwd", "") + self.get_path().removeprefix(Document.SEP)
        ext = self.get_extension().lower()

        if name == "":
            return

        full_path = path + name + "." + ext

        file = Path(full_path)
        try:
            file.touch()
        except FileExistsError:
            pass

        with open(full_path, "w", newline="\n") as file:
            file.write(self.cd.text)

        EventRegister.send(ClosingEvent(), "Tool")




