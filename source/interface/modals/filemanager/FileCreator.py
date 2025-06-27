from source.comms import Database
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import create_file
from source.filesystem.documents import Document
from source.interface.modals.filemanager.complex import FileDialog


class FileCreator(FileDialog):
    def __init__(self):
        super().__init__(["a8088", "ijvm"])
        self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        path = Database.FOLDER.getValue() + self.get_path().removeprefix(Document.SEP)
        ext = self.get_extension().lower()
        if not create_file(path, name, ext):
            self._name.setText("NewFile")
        else:
            EventRegister.send(ClosingEvent(), "Tool")
