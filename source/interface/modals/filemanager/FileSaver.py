from pathlib import Path

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import resolve_app_path
from source.filesystem.documents import Document, FT
from source.interface.modals.Popup import Popup
from source.interface.modals.filemanager.complex import FileDialog
from source.interface.shared import Settings
from source.interface.templates import create_toast


class FileSaver(FileDialog):
    def __new__(cls, *args, **kwargs):
        if Settings.get("editor/current", None):
            return super().__new__(cls)
        return None

    def __init__(self):
        if path := Settings.get("editor/current", None):
            self.cd: Document = Document(path)
            extension = self.cd.getExtension().lower()
            file_type = FT.findByExt(extension) or FT.FIJVM
            super().__init__(file_type.extensions, name=self.cd.getName())
            self._ext_picker.setCurrentText(extension.upper())
            self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        path = resolve_app_path(self.get_path())
        ext = self.get_extension().lower()

        if name == "":
            return

        destination = Path(path) / f"{name}.{ext}"
        window = self.window()

        try:
            if destination.is_dir():
                raise IsADirectoryError(f'"{destination.name}" is a folder.')
            overwrite = destination.exists() or destination.is_symlink()
            if overwrite and not Popup.ask(
                window,
                "Replace existing file?",
                f'A file named "{destination.name}" already exists. Do you want to replace it?',
                "Replace",
            ):
                return

            text = self.cd.text
            with destination.open("w" if overwrite else "x", newline="\n") as file:
                file.write(text)
        except (OSError, UnicodeError) as error:
            create_toast(window, str(error), "error")
            return

        EventRegister.send(ClosingEvent(), "Tool")




