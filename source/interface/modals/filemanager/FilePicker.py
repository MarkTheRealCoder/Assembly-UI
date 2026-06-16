import os

from PyQt5.QtWidgets import QFrame, QFileDialog, QSizePolicy, QVBoxLayout

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem.documents import FT
from source.interface.modals.filemanager.paths import PathTree
from source.interface.shared import createLayout, Settings
from source.platform import isMac


def pick_file(parent):
    if isMac():
        current = Settings.get("application/cwd", "")
        start = current if current and os.path.isdir(current) else os.path.expanduser("~")
        path, _ = QFileDialog.getOpenFileName(
            parent,
            "Open a File",
            start,
            f"Assembly Files (*.{FT.FIJVM} *.{FT.F8088});;All Files (*)",
        )
        if path:
            Settings.set("editor/current", path)
        return

    from source.interface.modals import modalOpen

    modalOpen(parent, FilePicker(), "Open a File")


class FilePicker(QFrame):
    def __init__(self):
        super().__init__(None)

        self.___tree = PathTree(self, True)
        self.___tree.onDoubleClick(self.set_path)

        self.configurations()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.addWidget(self.___tree)
        layout.setStretch(0, 1)
        self.setLayout(layout)

    def set_path(self, path: str, is_file: bool):
        if is_file:
            Settings.set("editor/current", path)
            EventRegister.send(ClosingEvent(), "Tool")
