from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow

from source.comms.events import ClosingEvent
from source.comms.events import ReadyEvent
from source.comms.handlers import EventRegister
from source.filesystem.DataManager import HandleJson
from source.interface.MainWidget import MainWidget
from source.platform import Desktop


class MainWindowGraphics(QMainWindow):
    def __init__(self):
        super(QMainWindow, self).__init__(None)
        self.setObjectName("MainWindow")
        self.defineWindowSize()
        self.setWindowTitle("Assembly Stdio")
        self.setFocusPolicy(Qt.FocusPolicy.ClickFocus)
        mwt: MainWidget = MainWidget(self)
        self.setCentralWidget(mwt)
        mwt.update()
        mwt.repaint()

    def centerOnScreen(self):
        screen_geometry = Desktop.getDesktopSize()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)

    def defineWindowSize(self):
        self.setMinimumSize(Desktop.sizeHint(3 / 4, 3 / 4))
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.centerOnScreen()


class MainWindowLogic(MainWindowGraphics):
    def __init__(self):
        super().__init__()


@EventRegister.register(ClosingEvent, priority=EventRegister.LOW)
class MainWindow(MainWindowLogic):
    def __init__(self):
        super().__init__()
        #self.resizeEventHandler = Resizer(self, "Main")

    def onClosingEvent(self, event):
        self.close()

    def showEvent(self, event):
        hj = HandleJson.get_instance()
        hj.get_cwd()
        hj.get_font()
        super().showEvent(event)
        EventRegister.send(ReadyEvent(), arg="Main")

    def event(self, event):
        return super().event(event)