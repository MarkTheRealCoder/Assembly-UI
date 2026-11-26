from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.interface import createLayout, Settings
from source.interface.modals import modalOpen
from source.interface.modals.filemanager.paths import PathTree
from source.interface.templates import toast_safe_exec


def open_file(window):
    """Open the file picker in a modal window."""
    toast_safe_exec(window, lambda: modalOpen(window, FilePicker(), "Open a File"))()


class FilePicker(QFrame):
    """File tree that opens the file double clicked."""
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
