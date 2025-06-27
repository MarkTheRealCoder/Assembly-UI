from pathlib import Path

from source.comms import Database
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem.documents.Document import Document
from source.interface.modals.filemanager.complex import FileDialog


class FileSaver(FileDialog):
    def __init__(self):
        self.cd: Document = Database.CURRENT_FILE.getValue()
        exts = ["ijvm", "jas"]
        if Database.DOCTYPE.getValue() == 2:
            exts = ["a8088", "s"]
        super().__init__(exts, name=self.cd.getName())
        self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        path = Database.FOLDER.getValue() + self.get_path().removeprefix(Document.SEP)
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




