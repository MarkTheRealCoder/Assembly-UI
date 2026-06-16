from pathlib import Path
import os

from PyQt5.QtWidgets import QFileDialog

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import resolve_app_path
from source.filesystem.documents import Document, FT
from source.interface.modals.filemanager.complex import FileDialog
from source.interface.shared import Settings
from source.platform import isMac


def _save_as_filter(doc_extension: str) -> tuple[str, set[str], str]:
    if FT.findByExt(doc_extension) == FT.F8088:
        default_ext = str(FT.F8088)
        return (
            f"8088 Files (*.{FT.F8088});;ASM Files (*.asm)",
            {default_ext, "asm"},
            default_ext,
        )
    default_ext = str(FT.FIJVM)
    return (
        f"IJVM Files (*.{FT.FIJVM});;JAS Files (*.jas)",
        {default_ext, "jas"},
        default_ext,
    )


def save_file_as(parent):
    current_path = Settings.get("editor/current", None)
    if not current_path:
        from source.interface.templates import create_toast

        create_toast(parent, "There is no file to save!", "error")
        return

    if isMac():
        doc = Document(current_path)
        start_dir = os.path.dirname(current_path)
        if not start_dir or not os.path.isdir(start_dir):
            cwd = Settings.get("application/cwd", "")
            start_dir = cwd if cwd and os.path.isdir(cwd) else os.path.expanduser("~")
        default_path = os.path.join(start_dir, f"{doc.getName()}.{doc.getExtension()}")
        filter_str, allowed_exts, default_ext = _save_as_filter(doc.getExtension())
        save_path, _ = QFileDialog.getSaveFileName(
            parent,
            "Save the current file as ...",
            default_path,
            filter_str,
        )
        if not save_path:
            return
        save_path = os.path.normpath(save_path)
        ext = os.path.splitext(save_path)[1].lstrip(".").lower()
        if ext not in allowed_exts:
            save_path = f"{save_path}.{default_ext}"
        with open(save_path, "w", newline="\n") as file:
            file.write(doc.text)
        return

    from source.interface.modals import modalOpen

    fs = FileSaver()
    if fs is None:
        from source.interface.templates import create_toast

        create_toast(parent, "There is no file to save!", "error")
        return
    modalOpen(parent, fs, "Save the current file as ...")


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




