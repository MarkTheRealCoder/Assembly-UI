from PyQt5.QtCore import Qt, pyqtProperty
from PyQt5.QtGui import QColor, QPainter, QFontMetrics

from source.filesystem import open_dir
from source.interface import Settings
from source.interface.templates import Title as BaseTitle, Tooltip
from source.platform import Desktop, isMac


class Title(BaseTitle):
    def __init__(self, parent):
        super().__init__(parent)
        self._hover_color = QColor()
        # Qt repaints the title when the pointer enters or leaves it.
        self.setAttribute(Qt.WA_Hover)
        Settings.addNotificationGroup("application/cwd", self.setLabel)
        self.FIXED_TEXT = "Assembly Stdio"
        self.setupFontAndAlignment()
        fm = QFontMetrics(self.font())
        self.setMinimumWidth(fm.horizontalAdvance(self.FIXED_TEXT) + 16)
        
        self.___curr_dir = None

        self.setActionOn("LeftDoubleClick", self.maximizeWindow)
        self.setActionOn("LeftCtrlClick", lambda: open_dir(self.___curr_dir))
        self._tooltip = Tooltip(self, "")
        self._tooltip.setPosition("below", "center")
        self._tooltip.setFollowing("widget")
        self.setLabel()

    def setupFontAndAlignment(self):
        font = Desktop.createScalableFont("Anonymous Pro", 12, False)
        self.setFont(font)
        
        self.setAlignment(Qt.AlignCenter)

    def maximizeWindow(self):
        """Toggle window maximize/restore state"""
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()

    def setLabel(self):
        self.___curr_dir = Settings.get("application/cwd", "Select a working directory")
        self.setText(f"Assembly Stdio - {self.___curr_dir}")
        modifier = "Cmd" if isMac() else "Ctrl"
        self._tooltip.setText(f"Current directory: {self.___curr_dir}\n\nDouble Click to Maximize/Restore | {modifier}+Click to Open Folder")

    @pyqtProperty(QColor)
    def hoverColor(self):
        return self._hover_color

    @hoverColor.setter
    def hoverColor(self, color):
        self._hover_color = color
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        if self.underMouse() and self._hover_color.isValid():
            painter.setPen(self._hover_color)
        metrics = QFontMetrics(self.font())
        elided = metrics.elidedText(self.text(), Qt.ElideRight, self.width())
        painter.drawText(self.rect(), self.alignment(), elided)