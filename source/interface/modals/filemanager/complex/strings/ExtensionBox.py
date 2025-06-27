from PyQt5.QtWidgets import QComboBox, QSizePolicy

from source.filesystem.IconManager import IconManager


class ExtensionBox(QComboBox):
    def __init__(self, parent, extensions: list[str]):
        super().__init__(parent)
        self.setObjectName("ExtensionBox")

        for extension in extensions:
            self.addItem(IconManager.getInstance().getIcon(extension), extension.upper())

        self.setFixedHeight(30)
        self.setFixedWidth(100)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
