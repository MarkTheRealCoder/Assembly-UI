from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout
from regex import regex

from src.filesystem.Folder import create_dir, open_dir
from src.filesystem.documents.Document import Document
from src.interface.commons.Commons import createLayout
from src.interface.external.Dialog import Dialog
from src.interface.external.filemanager.complex.buttons.ConfirmButton import ConfirmButton
from src.interface.external.filemanager.complex.buttons.FolderButton import FolderButton
from src.interface.external.filemanager.complex.buttons.HomeButton import HomeButton
from src.interface.external.filemanager.complex.buttons.OpenFolderButton import OpenFolderButton
from src.interface.external.filemanager.complex.strings.ExtensionBox import ExtensionBox
from src.interface.external.filemanager.complex.strings.FileBox import FileBox
from src.interface.external.filemanager.complex.strings.PathBox import PathBox
from src.interface.external.filemanager.paths.PathTree import PathTree
from src.signals.Variables import DataBase


class FileComplex(QFrame):
    def __init__(self, extensions: list[str], **kwargs):
        super().__init__(None)

        self.___dialog = None
        self.___tree = PathTree(self, True)
        self.___box = PathBox(self)
        self.___name = FileBox(self, **kwargs)

        self.___home = HomeButton(self)
        self.___open_folder = OpenFolderButton(self)
        self.___create_folder = FolderButton(self)
        self.confirm = ConfirmButton(self)

        self.___ext_picker = ExtensionBox(self, extensions)

        self.configurations()
        self.configure_components()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout, self)
        blayout: QHBoxLayout = createLayout(QHBoxLayout, self)

        tlayout.addWidget(self.___home, 1)
        tlayout.addWidget(self.___box)
        tlayout.addWidget(self.___open_folder, 1)
        tlayout.addWidget(self.___create_folder, 1)

        blayout.addWidget(self.___name)
        blayout.addWidget(self.___ext_picker)
        blayout.addWidget(self.confirm, 1)

        layout.addLayout(tlayout)
        layout.addWidget(self.___tree)
        layout.addLayout(blayout)
        layout.setStretch(0, 1)
        self.setLayout(layout)

    def configure_components(self):
        self.___tree.onClick(self.set_current_path)
        self.___box.onEditing(self.validate)
        self.___home.onClick(self.reset_current_path)
        self.___open_folder.onClick(self.open_folder)
        self.___create_folder.onClick(self.create_folder)

    def validate(self, path: str):
        if path.startswith(Document.SEP) and path.endswith(Document.SEP):
            print("Tutto Ok")
        else:
            print("Errore")
            self.___box.setText(Document.SEP + path)

    def set_current_path(self, path: str, is_file: bool):
        if is_file:
            name = regex.match(f".*\\{Document.SEP}(\\w+)\\.\\w+", path).group(1)
            self.___name.setText(name)
        else:
            rp = Document.SEP + path.removeprefix(DataBase.FOLDER.getValue()) # Referred path
            self.___box.setText(rp)

    def create_folder(self):
        def create_folder(name: str) -> bool:
            return create_dir(DataBase.FOLDER.getValue() + self.___box.text().removeprefix(Document.SEP), name)

        self.___dialog = Dialog(self, "Create Folder", "Insert the folder name", create_folder)

    def reset_current_path(self):
        self.___box.setText(Document.SEP)

    def open_folder(self):
        open_dir(DataBase.FOLDER.getValue() + self.___box.text().removeprefix(Document.SEP))

    def get_path(self) -> str:
        return self.___box.text()

    def get_name(self) -> str:
        return self.___name.text()

    def get_extension(self) -> str:
        return self.___ext_picker.currentText()
