import ctypes

from PyQt5.QtCore import Qt, QRect, QSize, QEvent
from PyQt5.QtWidgets import QMainWindow

from source.comms.events import ClosingEvent
from source.comms.events import ReadyEvent
from source.comms.handlers import EventRegister
from source.interface.MainWidget import MainWidget
from source.interface.shared import Settings
from source.platform import Desktop


class MainWindowGraphics(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__(None)
        self.setObjectName("MainWindow")
        self.defineWindowSize()
        self.setWindowTitle("Assembly Stdio")
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        self.setAttribute(Qt.WA_TranslucentBackground, True)
        mwt: MainWidget = MainWidget(self)
        self.setFocusProxy(mwt)
        self.setCentralWidget(mwt)
        mwt.update()
        mwt.repaint()

    def centerOnScreen(self):
        screen_geometry = Desktop.getDesktopSize()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def defineWindowSize(self):
        self.setMinimumSize(QSize(800, 600))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.centerOnScreen()


class MainWindowLogic(MainWindowGraphics):
    def __init__(self):
        self.corners = []
        super().__init__()

    def registerCorner(self, corner):
        self.corners.append(corner)


@EventRegister.register(ClosingEvent, priority=EventRegister.LOW)
class MainWindow(MainWindowLogic):
    def __init__(self):
        super().__init__()

    def onClosingEvent(self, event):
        isMaximized = self.isFullScreen() or self.isMaximized()
        Settings.silentSet("mainwindow/fullscreen", isMaximized)
        if not isMaximized:
            Settings.silentSet("mainwindow/size", self.size())
        Settings.sync()
        event.accept()
        self.close()

    def showEvent(self, event):
        self.resize(Settings.get("mainwindow/size", self.minimumSize()))
        if Settings.get("mainwindow/fullscreen", False, _type=bool):
            for corner in self.corners:
                corner.hide()
            self.showMaximized()
            Settings.set("mainwindow/fullscreen", True)
        super().showEvent(event)
        EventRegister.send(ReadyEvent(), arg="Main")

    def event(self, event):
        return super().event(event)

    def resizeEvent(self, event):
        if self.isMaximized() or self.isFullScreen():
            for corner in self.corners:
                corner.hide()
        elif not self.isMinimized():
            for corner in self.corners:
                corner.show()

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if event.oldState() & Qt.WindowMinimized:
                if Settings.get("mainwindow/fullscreen", False, _type=bool):
                    self.showNormal()
                    self.update()
                    self.showMaximized()
                    self.update()
        return super().changeEvent(event)


def get_available_geometry():
    # Get working area (screen minus taskbar)
    spi_get_work_area = 0x0030
    rect = ctypes.wintypes.RECT()
    ctypes.windll.user32.SystemParametersInfoW(spi_get_work_area, 0, ctypes.byref(rect), 0)
    return QRect(rect.left, rect.top, rect.right - rect.left, rect.bottom - rect.top)
