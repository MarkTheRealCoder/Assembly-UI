from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy

from source.filesystem import find_path
from source.interface.templates import GenericButton, Tooltip


class Button(GenericButton):
    def __init__(self, parent, icon_path: str, tooltip: str):
        super().__init__(parent)

        self.setObjectName("FileButton")
        # The macOS style otherwise removes its layout margins and the fixed-size widgets overlap.
        self.setAttribute(Qt.WA_LayoutUsesWidgetRect)
        self.setFixedHeight(30)
        self.setFixedWidth(30)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setIcon(self.rerenderIcon(QIcon(find_path(icon_path)), "#569CD6"))
        self.setIconSize(QSize(20, 20))

        self.tooltip = Tooltip(self, tooltip)
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

        self.___placeholder = lambda: None

        self.clicked.connect(lambda: self.___placeholder())

    def onClick(self, func: callable):
        if not callable(func):
            raise TypeError("func must be callable")
        self.___placeholder = func