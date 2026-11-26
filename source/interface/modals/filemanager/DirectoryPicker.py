from PyQt5.QtCore import QModelIndex, QPersistentModelIndex
from PyQt5.QtWidgets import QFrame, QHBoxLayout, QSizePolicy, QVBoxLayout

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import create_dir
from source.interface import createLayout, Settings
from source.interface.modals import Dialog
from source.interface.modals.filemanager.complex import Button
from source.interface.modals.filemanager.complex.strings import PathBox
from source.interface.modals.filemanager.paths import PathTree


class DirectoryPickerGraphics(QFrame):
    def __init__(self):
        super().__init__(None)

        self._tree = PathTree(self)
        self._box = PathBox(self)
        self._box.clear()
        self._box.setPlaceholderText("Select a folder")
        self._create_folder = Button(self, "new_folder.svg", "Create a folder inside the selected one")
        self._create_folder.setEnabled(False)

        self.configurations()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        controls: QHBoxLayout = createLayout(QHBoxLayout)

        controls.addWidget(self._box, 1)
        controls.addWidget(self._create_folder)

        layout.setSpacing(10)
        layout.addLayout(controls)
        layout.addWidget(self._tree, 1)
        self.setLayout(layout)


class DirectoryPickerLogic(DirectoryPickerGraphics):
    def __init__(self):
        super().__init__()
        self._dialog = None
        self._selected_path = None

    def sync_selection(self):
        indexes = self._tree.selectionModel().selectedIndexes()
        self._selected_path = self._tree.get_path(indexes[0])[0] if indexes else None
        self._box.setText(self._selected_path or "")
        self._create_folder.setEnabled(self._selected_path is not None)

    def create_folder(self):
        indexes = self._tree.selectionModel().selectedIndexes()
        if not indexes:
            return
        path = self._selected_path
        parent = QPersistentModelIndex(indexes[0])

        def create(name: str) -> bool:
            if not create_dir(path, name):
                return False
            if parent.isValid():
                self._tree.reveal_child(QModelIndex(parent), name)
            return True

        self._dialog = Dialog(self, "Create Folder", "Insert the folder name", create,
                              "Could not create the folder. Check the name and try again.")


class DirectoryPicker(DirectoryPickerLogic):
    """Folder tree where a double click sets the working directory."""
    def __init__(self):
        super().__init__()
        self._tree.selectionModel().selectionChanged.connect(self.sync_selection)
        self._tree.onDoubleClick(self.set_path)
        self._create_folder.onClick(self.create_folder)

    def set_path(self, path: str, is_file: bool):
        if not is_file:
            Settings.set("application/cwd", path)
            EventRegister.send(ClosingEvent(), "Tool")
