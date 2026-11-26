from pathlib import Path

from source.comms import Database
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import create_file, resolve_app_path
from source.interface import Settings
from source.interface.modals.filemanager.complex import FileDialog
from source.interface.templates import create_toast


class FileCreator(FileDialog):
    """Dialog that creates a file in the chosen folder and opens it, asking before replacing an existing one."""
    def __init__(self):
        super().__init__(["a8088", "ijvm"])
        self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        if not name.strip():
            return
        path = resolve_app_path(self.get_path())
        ext = self.get_extension().lower()
        destination = Path(path) / f"{name}.{ext}"
        window = self.window()

        try:
            if destination.exists() or destination.is_symlink():
                if not self.confirm_replace(destination):
                    return
                destination.write_bytes(b"")
                Database.ON_FILE_REPLACED.setValue(str(destination))
                file = destination
            else:
                file = create_file(path, name, ext)
        except OSError as error:
            create_toast(window, str(error), "error")
            return

        if file is None:
            create_toast(window, f'Could not create "{destination.name}".', "error")
            return
        Settings.set("editor/current", str(file))
        EventRegister.send(ClosingEvent(), "Tool")
