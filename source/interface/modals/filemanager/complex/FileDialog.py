import os
from collections.abc import Sequence
from pathlib import Path

from PyQt5.QtWidgets import QFrame, QSizePolicy, QVBoxLayout, QHBoxLayout

from source.filesystem import create_dir, open_dir, resolve_app_path, to_ui_path
from source.filesystem.documents import Document
from source.interface import createLayout
from source.interface.modals import Dialog, Popup
from source.interface.modals.filemanager.complex.Button import Button
from source.interface.modals.filemanager.complex.strings import ExtensionBox, FileBox, PathBox
from source.interface.modals.filemanager.paths import PathTree


class FileDialogGraphics(QFrame):
    def __init__(self, extensions: Sequence[str], **kwargs):
        super().__init__(None)

        self._dialog = None

        self._tree = PathTree(self, True)
        self._box = PathBox(self)
        self._name = FileBox(self, **kwargs)

        self._home = Button(self, "home.svg", "Set current path to home")

        self._open_folder = Button(self, "open_folder.svg", "Open folder path")
        self._create_folder = Button(self, "new_folder.svg", "Create new folder")
        self.confirm = Button(self, "confirm.svg", "Confirm choices")

        self._ext_picker = ExtensionBox(self, extensions)

        self.configurations()

    def configurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        tlayout: QHBoxLayout = createLayout(QHBoxLayout)
        blayout: QHBoxLayout = createLayout(QHBoxLayout)

        tlayout.addWidget(self._home)
        tlayout.addWidget(self._box, 1)
        tlayout.addWidget(self._open_folder)
        tlayout.addWidget(self._create_folder)

        blayout.addWidget(self._name, 1)
        blayout.addWidget(self._ext_picker)
        blayout.addWidget(self.confirm)

        layout.setSpacing(10)
        layout.addLayout(tlayout)
        layout.addWidget(self._tree)
        layout.addLayout(blayout)
        layout.setStretch(0, 1)
        self.setLayout(layout)


class FileDialogLogic(FileDialogGraphics):
    def __init__(self, extensions: Sequence[str], **kwargs):
        super().__init__(extensions, **kwargs)

    def validate(self, path: str):
        if not (path.startswith(Document.SEP) and path.endswith(Document.SEP)):
            self._box.setText(Document.SEP + path)

    def confirm_replace(self, destination: Path) -> bool:
        """Ask whether to replace destination and return the answer. Raise IsADirectoryError if it is a folder."""
        if destination.is_dir():
            raise IsADirectoryError(f'"{destination.name}" is a folder.')
        accepted = Popup.ask(
            self.window(),
            "Replace existing file?",
            f'A file named "{destination.name}" already exists. Do you want to replace it?',
            "Replace",
        )
        if not accepted:
            self._name.setFocus()
            self._name.selectAll()
        return accepted

    def set_current_path(self, path: str, is_file: bool):
        if is_file:
            path, filename = os.path.split(path)
            name, extension = os.path.splitext(filename)
            self._name.setText(name)
            self._ext_picker.setCurrentText(extension[1:].upper())
        self._box.setText(to_ui_path(path))

    def create_folder(self):
        def create_folder(name: str) -> bool:
            return create_dir(resolve_app_path(self._box.text()), name)

        self._dialog = Dialog(self, "Create Folder", "Insert the folder name", create_folder,
                              "Could not create the folder. Check the name and try again.")

    def reset_current_path(self):
        self._box.setText(Document.SEP)

    def open_folder(self):
        open_dir(resolve_app_path(self._box.text()))

    def get_path(self) -> str:
        return self._box.text()

    def get_name(self) -> str:
        return self._name.text()

    def get_extension(self) -> str:
        return self._ext_picker.currentText()


class FileDialog(FileDialogLogic):
    """Base dialog with a folder tree and path, name and extension fields, shared by the file creation and save dialogs."""
    def __init__(self, extensions: Sequence[str], **kwargs):
        super().__init__(extensions, **kwargs)
        self._tree.onClick(self.set_current_path)
        self._box.onEditing(self.validate)
        self._home.onClick(self.reset_current_path)
        self._open_folder.onClick(self.open_folder)
        self._create_folder.onClick(self.create_folder)
        self._name.returnPressed.connect(self.confirm.click)
