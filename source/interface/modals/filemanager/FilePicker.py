from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from source.comms.Signals import DataBase
from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.interface.modals.filemanager.paths import PathTree
from source.interface.shared import createLayout


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
            DataBase.OPEN_FILE.setValue(path)
            EventRegister.send(ClosingEvent(), "Tool")
