from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from source.filesystem import open_dir
from source.interface.shared import Settings
from source.interface.templates import Title as BaseTitle
from source.interface.templates import Tooltip
from source.platform import Desktop


class Title(BaseTitle):
    def __init__(self, parent, mw: QMainWindow):
        super().__init__(parent, mw)
        Settings.addNotificationGroup("application/cwd", self.setLabel)
        self.setupFontAndAlignment()
        
        self.___curr_dir = None
        self.setLabel()

        self.setActionOn("LeftDoubleClick", self.maximizeWindow)
        self.setActionOn("LeftCtrlClick", lambda: open_dir(self.___curr_dir))
        self._tooltip = Tooltip(self, "Double Click to Maximize/Restore | Ctrl+Click to Open Folder")
        self._tooltip.setPosition("below", "center")
        self._tooltip.setFollowing("widget")

    def setupFontAndAlignment(self):
        # Set scalable font
        font = Desktop.createScalableFont("Anonymous Pro", 12, False)
        self.setFont(font)
        
        # Ensure center alignment
        self.setAlignment(Qt.AlignCenter)

    def maximizeWindow(self):
        """Toggle window maximize/restore state"""
        if self.mw.isMaximized():
            self.mw.showNormal()
        else:
            self.mw.showMaximized()

    def setLabel(self):
        self.___curr_dir = Settings.get("application/cwd", "Select a working directory")
        self.setText(f"Assembly Stdio - {self.___curr_dir}")