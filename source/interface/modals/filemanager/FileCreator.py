from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import create_file
from source.filesystem.documents import Document
from source.interface.modals.filemanager.complex import FileDialog
from source.interface.shared import Settings


class FileCreator(FileDialog):
    def __init__(self):
        super().__init__(["a8088", "ijvm"])
        self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        path = Settings.get("application/cwd") + self.get_path().removeprefix(Document.SEP)
        ext = self.get_extension().lower()
        if file := create_file(path, name, ext):
            Settings.set("editor/current", str(file))
            EventRegister.send(ClosingEvent(), "Tool")
        else:
            self._name.setText("NewFile")
