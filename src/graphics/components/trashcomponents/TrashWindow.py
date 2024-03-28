from PyQt5.QtCore import QEvent, QRect, QPoint, QObject, Qt
from PyQt5.QtWidgets import QDesktopWidget, QMainWindow, QLabel, QPushButton, QFrame, QHBoxLayout, QVBoxLayout, \
    QSizePolicy

from src.tools.Tools import find_path, createLayout


def wOpen(anywidget=None, size: tuple = (400, 450)):
    tw = TrashWindow(anywidget, size)
    tw.show()


class TrashWindow(QMainWindow):

    def __init__(self, widget, size: tuple = (300, 300)):
        super(QMainWindow, self).__init__()
        self.setObjectName("Trash")
        self.setConfigurations(size)
        self.___widget = widget
        self.frame = QFrame(self)

        self.setMainWidget(widget)

        self.setCentralWidget(self.frame)

    def setConfigurations(self, size: tuple):
        self.setWindowFlag(Qt.FramelessWindowHint, True)
        self.setWindowFlag(Qt.Tool, True)
        self.setMinimumWidth(size[0])
        self.setMinimumHeight(size[1])
        self.centerOnScreen()

        with open(find_path("trash.qss"), "r") as f:
            self.setStyleSheet(f.read())

    def setMainWidget(self, widget):
        widget.setParent(self.frame)

        ml: QVBoxLayout = createLayout(QVBoxLayout, self.frame)
        tl: QHBoxLayout = createLayout(QHBoxLayout, self.frame)

        ml.addLayout(tl)
        ml.addWidget(widget)
        tl.addWidget(TrashLabel(self.frame, self))
        tl.addWidget(TrashButton(self.frame, self))

        tl.setStretch(0, 5)
        tl.setStretch(1, 1)

    def centerOnScreen(self):
        desktop = QDesktopWidget()
        screen_geometry = desktop.screenGeometry()
        x = (screen_geometry.width() - self.width()) // 2
        y = (screen_geometry.height() - self.height()) // 2
        self.move(x, y)


class TrashLabel(QLabel):
    movable: bool = False

    def __init__(self, parent, mw: QMainWindow):
        super(QLabel, self).__init__(parent)
        self.mw: QMainWindow = mw
        self.setObjectName("Label")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)
        self.setFixedHeight(30)
        self.__mousePressPos = 0
        self.__mouseMovePos = 0
        self.installEventFilter(self)

    def eventFilter(self, o: QObject, e: QEvent) -> bool:
        if hasattr(e, "button") and e.button() == Qt.LeftButton:
            if e.type() == QEvent.MouseButtonPress:
                TrashLabel.movable = True
                self.__mousePressPos = e.globalPos()
                self.__mouseMovePos = e.globalPos()
            elif e.type() == QEvent.MouseButtonRelease:
                TrashLabel.movable = False
        elif e.type() == QEvent.MouseMove and TrashLabel.movable:
            self.moveWindow(e)

        return super().eventFilter(o, e)

    def moveWindow(self, e: QEvent):
        desk = QDesktopWidget()
        screen_rect: QRect = desk.availableGeometry()
        del desk
        bottom_right: QPoint = screen_rect.bottomRight()
        globalPos = e.globalPos()
        diff = globalPos - self.__mouseMovePos
        self.__mouseMovePos = globalPos
        curr_pos: QPoint = self.mw.pos()
        if (curr_pos.y() + diff.y()) < bottom_right.y() - 15:
            self.mw.move(curr_pos + diff)


class TrashButton(QPushButton):
    def __init__(self, parent, mw: QMainWindow):
        super(QPushButton, self).__init__(parent)
        self.mw: QMainWindow = mw
        self.setFixedHeight(30)
        self.setText("x")
        self.setObjectName("Button")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.MinimumExpanding)

    def mousePressEvent(self, e: QEvent):
        self.mw.destroy(True, True)
        self.mw.close()


# TODO: Aggiungere una variabile globale che tenga traccia dell'istanza della TrashWindow
# TODO: Cambiare i "destroy" e "close" con deleteLater()
