import os
from pathlib import Path

from PyQt5.QtWidgets import QFileDialog

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import create_file, resolve_app_path
from source.filesystem.documents import FT
from source.interface.modals.filemanager.complex import FileDialog
from source.interface.shared import Settings
from source.platform import isMac


def pick_new_file(parent):
    if isMac():
        current = Settings.get("application/cwd", "")
        start_dir = current if current and os.path.isdir(current) else os.path.expanduser("~")
        path, _ = QFileDialog.getSaveFileName(
            parent,
            "Create a New File",
            os.path.join(start_dir, f"NewFile.{FT.FIJVM}"),
            f"IJVM Files (*.{FT.FIJVM});;8088 Files (*.{FT.F8088})",
        )
        if not path:
            return
        path = os.path.normpath(path)
        ext = os.path.splitext(path)[1].lstrip(".").lower()
        if ext not in {str(FT.FIJVM), str(FT.F8088)}:
            path = f"{path}.{FT.FIJVM}"
        file = Path(path)
        if not file.exists():
            file.touch()
        Settings.set("editor/current", str(file))
        return

    from source.interface.modals import modalOpen

    modalOpen(parent, FileCreator(), "Create a New File")


class FileCreator(FileDialog):
    def __init__(self):
        super().__init__(["a8088", "ijvm"])
        self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        path = resolve_app_path(self.get_path())
        ext = self.get_extension().lower()
        if file := create_file(path, name, ext):
            Settings.set("editor/current", str(file))
            EventRegister.send(ClosingEvent(), "Tool")
        else:
            self._name.setText("NewFile")
