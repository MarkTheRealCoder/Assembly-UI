
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtWidgets import QMainWindow

from source.comms.events import ClosingEvent
from source.comms.events import ReadyEvent
from source.comms.handlers import EventRegister
from source.interface.MainWidget import MainWidget
from source.interface.shared import Settings
from source.interface.templates.window import BaseWindow


class MainWindowGraphics(QMainWindow, BaseWindow):
    def __init__(self):
        super(QMainWindow, self).__init__(None)
        self.setObjectName("MainWindow")
        self.setWindowTitle("Assembly Stdio")
        self.setFrameless()
        mwt: MainWidget = MainWidget(self)
        self.setCentralWidget(mwt)
        mwt.update()
        mwt.repaint()


class MainWindowLogic(MainWindowGraphics):
    def __init__(self):
        super().__init__()


@EventRegister.register(ClosingEvent, priority=EventRegister.LOW)
class MainWindow(MainWindowLogic):
    def __init__(self):
        super().__init__()
        self.___first_time = True

    def onClosingEvent(self, event):
        isMaximized = self.isFullScreen() or self.isMaximized()
        Settings.silentSet("mainwindow/fullscreen", isMaximized)
        if not isMaximized:
            Settings.silentSet("mainwindow/size", self.size())
        Settings.sync()
        event.accept()
        self.close()

    def showEvent(self, event):
        if self.___first_time:
            self.___first_time = False
            self.resize(Settings.get("mainwindow/size", self.minimumSize()))
            if Settings.get("mainwindow/fullscreen", False, _type=bool):
                self.showMaximized()
                Settings.set("mainwindow/fullscreen", True)
            super().showEvent(event)
            EventRegister.send(ReadyEvent(), arg="Main")
        else:
            super().showEvent(event)

    def event(self, event):
        return super().event(event)

    def changeEvent(self, event):
        if event.type() == QEvent.WindowStateChange:
            if event.oldState() & Qt.WindowMinimized:
                if Settings.get("mainwindow/fullscreen", False, _type=bool):
                    self.showMaximized()
            Settings.set("mainwindow/fullscreen", self.isMaximized())
        return super().changeEvent(event)


