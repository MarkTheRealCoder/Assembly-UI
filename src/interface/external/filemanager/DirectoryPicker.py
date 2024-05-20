from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout

from src.eventhandlers.Register import EventRegister
from src.events.data.ClosingEvent import ClosingEvent
from src.interface.commons.Commons import createLayout
from src.interface.external.filemanager.paths.PathTree import PathTree
from src.signals.Variables import DataBase


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
            DataBase.FOLDER.setValue(path)
            EventRegister.send(ClosingEvent(), "Tool")