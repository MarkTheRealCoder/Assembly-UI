import os

from PyQt5.QtWidgets import QFrame, QFileDialog, QSizePolicy, QVBoxLayout

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.interface.modals.filemanager.paths import PathTree
from source.interface.shared import createLayout, Settings
from source.platform import isMac


def pick_working_directory(parent):
    if isMac():
        current = Settings.get("application/cwd", "")
        start = current if current and os.path.isdir(current) else os.path.expanduser("~")
        path = QFileDialog.getExistingDirectory(
            parent,
            "Setup Working Directory",
            start,
            QFileDialog.ShowDirsOnly | QFileDialog.DontResolveSymlinks,
        )
        if path:
            Settings.set("application/cwd", path)
        return

    from source.interface.modals import modalOpen

    modalOpen(parent, DirectoryPicker(), "Setup Working Directory")


class DirectoryPicker(QFrame):
    def __init__(self):
        super().__init__(None)

        self.___tree = PathTree(self)
        self.___tree.onDoubleClick(self.set_path)

        self.configurations()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        layout.addWidget(self.___tree)
        layout.setStretch(0, 1)
        self.setLayout(layout)

    def set_path(self, path: str, is_file: bool):
        if not is_file:
            Settings.set("application/cwd", path)
            EventRegister.send(ClosingEvent(), "Tool")