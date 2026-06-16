from PyQt5.QtCore import QSize, QTimer
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QSizePolicy

from source.filesystem import find_path
from source.interface.shared import Settings
from source.interface.templates import GenericButton
from source.platform.adaptability import isMac


class MaximizeButton(GenericButton):
    def __init__(self, parent, properties: dict[str, bool] = None):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Minimum)
        self.maximize_icon = self.rerenderIcon(QIcon(find_path("maximize.svg")), "#569CD6")
        self.restore_icon = self.rerenderIcon(QIcon(find_path("restore.svg")), "#569CD6")
        self.window().MAXBUTTON_RECT = lambda: self.get_rect()

        self.setIcon(self.maximize_icon)
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Maximize")

        Settings.addNotificationGroup("mainwindow/fullscreen", self.updateIcon)

        self.clicked.connect(self.on_press)

        self._tiling_target = None
        self._hover_menu_timer = QTimer(self)
        self._hover_menu_timer.setSingleShot(True)
        self._hover_menu_timer.setInterval(350)
        self._hover_menu_timer.timeout.connect(self._show_tiling_menu)

    def updateIcon(self):
        if Settings.get("mainwindow/fullscreen", False, bool):
            self.setIcon(self.restore_icon)
        else:
            self.setIcon(self.maximize_icon)

    def get_rect(self) -> tuple[int, int, int, int]:
        pos = self.mapTo(self.window(), self.rect().topLeft())
        return pos.x(), pos.y(), self.width(), self.height()

    def on_press(self):
        w = self.window()
        if not w.isMaximized():
            w.showMaximized()
            Settings.set("mainwindow/fullscreen", True)
        else:
            w.showNormal()
            Settings.set("mainwindow/fullscreen", False)

    def enterEvent(self, event):
        if isMac():
            self._hover_menu_timer.start()
        super().enterEvent(event)

    def leaveEvent(self, event):
        if isMac():
            self._hover_menu_timer.stop()
        super().leaveEvent(event)

    def _show_tiling_menu(self):
        if not isMac() or not self.isVisible() or not self.underMouse():
            return
        from source.interface.templates.window.macos_native import show_tiling_menu_at_widget

        self._tiling_target = show_tiling_menu_at_widget(self.window(), self)
