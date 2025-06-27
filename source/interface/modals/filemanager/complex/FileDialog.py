from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout
from regex import regex

from source.comms import Database
from source.filesystem import create_dir, open_dir
from source.filesystem.documents import Document
from source.interface.modals.Dialog import Dialog
from source.interface.modals.filemanager.complex.buttons import ConfirmButton
from source.interface.modals.filemanager.complex.buttons import FolderButton
from source.interface.modals.filemanager.complex.buttons import HomeButton
from source.interface.modals.filemanager.complex.buttons import OpenFolderButton
from source.interface.modals.filemanager.complex.strings import ExtensionBox
from source.interface.modals.filemanager.complex.strings import FileBox
from source.interface.modals.filemanager.complex.strings import PathBox
from source.interface.modals.filemanager.paths import PathTree
from source.interface.shared import createLayout


class FileDialogGraphics(QFrame):
    def __init__(self, extensions: list[str], **kwargs):
        super().__init__(None)

        self._dialog = None

        self._tree = PathTree(self, True)
        self._box = PathBox(self)
        self._name = FileBox(self, **kwargs)

        self._home = HomeButton(self)

        self._open_folder = OpenFolderButton(self)
        self._create_folder = FolderButton(self)
        self.confirm = ConfirmButton(self)

        self._ext_picker = ExtensionBox(self, extensions)

        self.configurations()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout, self)
        blayout: QHBoxLayout = createLayout(QHBoxLayout, self)

        tlayout.addWidget(self._home, 1)
        tlayout.addWidget(self._box)
        tlayout.addWidget(self._open_folder, 1)
        tlayout.addWidget(self._create_folder, 1)

        blayout.addWidget(self._name)
        blayout.addWidget(self._ext_picker)
        blayout.addWidget(self.confirm, 1)

        layout.addLayout(tlayout)
        layout.addWidget(self._tree)
        layout.addLayout(blayout)
        layout.setStretch(0, 1)
        self.setLayout(layout)


class FileDialogLogic(FileDialogGraphics):
    def __init__(self, extensions: list[str], **kwargs):
        super().__init__(extensions, **kwargs)

    def validate(self, path: str):
        if path.startswith(Document.SEP) and path.endswith(Document.SEP):
            print("Tutto Ok")
        else:
            print("Errore")
            self._box.setText(Document.SEP + path)

    def set_current_path(self, path: str, is_file: bool):
        if is_file:
            name = regex.match(f".*\\{Document.SEP}(\\w+)\\.\\w+", path).group(1)
            self._name.setText(name)
        else:
            rp = Document.SEP + path.removeprefix(Database.FOLDER.getValue()) # Referred path
            self._box.setText(rp)

    def create_folder(self):
        def create_folder(name: str) -> bool:
            return create_dir(Database.FOLDER.getValue() + self._box.text().removeprefix(Document.SEP), name)

        self._dialog = Dialog(self, "Create Folder", "Insert the folder name", create_folder)

    def reset_current_path(self):
        self._box.setText(Document.SEP)

    def open_folder(self):
        open_dir(Database.FOLDER.getValue() + self._box.text().removeprefix(Document.SEP))

    def get_path(self) -> str:
        return self._box.text()

    def get_name(self) -> str:
        return self._name.text()

    def get_extension(self) -> str:
        return self._ext_picker.currentText()


class FileDialog(FileDialogLogic):
    def __init__(self, extensions: list[str], **kwargs):
        super().__init__(extensions, **kwargs)
        self._tree.onClick(self.set_current_path)
        self._box.onEditing(self.validate)
        self._home.onClick(self.reset_current_path)
        self._open_folder.onClick(self.open_folder)
        self._create_folder.onClick(self.create_folder)
