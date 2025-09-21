from typing import Literal

from PyQt5.QtCore import Qt, QPoint, QSettings
from PyQt5.QtGui import QMouseEvent, QPainter, QColor, QPixmap, QIcon
from PyQt5.QtSvg import QSvgRenderer
from PyQt5.QtWidgets import QWidget, QLayout, QFrame, QSizePolicy, QGridLayout

from source.comms.Signals import Variable
from source.interface import MainWindow


class Settings:
    SETTINGS = QSettings("settings.ini", QSettings.IniFormat)
    SIGNAL = Variable(str)

    @staticmethod
    def get(key: str, default=None, _type: type = None):
        return Settings.SETTINGS.value(key, default) if _type is None else Settings.SETTINGS.value(key, default, _type)

    @staticmethod
    def set(key: str, value):
        """ Sets a value and emits the signal """
        Settings.SETTINGS.setValue(key, value)
        Settings.SIGNAL.setValue(key)

    @staticmethod
    def silentSet(key: str, value):
        """ Sets a value without emitting the signal """
        Settings.SETTINGS.setValue(key, value)

    @staticmethod
    def remove(key: str):
        """ Removes a setting """
        Settings.SETTINGS.remove(key)
        Settings.SETTINGS.sync()

    @staticmethod
    def beginGroup(name: str):
        """ Begins a new group """
        Settings.SETTINGS.beginGroup(name)

    @staticmethod
    def endGroup():
        """ Ends the current group """
        Settings.SETTINGS.endGroup()

    @staticmethod
    def addNotificationGroup(name: str, callback: callable):
        """ Calls the callback when a setting with the given name (or starting with it) changes """
        Settings.SIGNAL.connect(lambda: callback() if Settings.SIGNAL.getValue() == name else None)

    @staticmethod
    def sync():
        """ Syncs the settings to the file """
        Settings.SETTINGS.sync()



def createLayout(l: type, parent: QWidget):
    layout = l(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.setSizeConstraint(QLayout.SetNoConstraint)
    return layout


class DraggableFrame(QFrame):
    def __init__(self, parent, position: Literal["top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"]):
        super().__init__(parent)
        self.setObjectName("DraggableFrame")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        if position == "top":
            self.setCursor(Qt.SizeVerCursor)
            self.setFixedHeight(5)
        elif position == "bottom":
            self.setCursor(Qt.SizeVerCursor)
            self.setFixedHeight(5)
        elif position == "left":
            self.setCursor(Qt.SizeHorCursor)
            self.setFixedWidth(5)
        elif position == "right":
            self.setCursor(Qt.SizeHorCursor)
            self.setFixedWidth(5)
        else:
            if position == "topright" or position == "bottomleft":
                self.setCursor(Qt.SizeBDiagCursor)
            else:
                self.setCursor(Qt.SizeFDiagCursor)
            self.setFixedSize(5, 5)

        self.position = self.getPositionValue(position)
        self.drag_position = None
        self.main_window: MainWindow = parent.parent()
        if hasattr(self.main_window, "registerCorner"):
            self.main_window.registerCorner(self)

    def getPositionValue(self, position: Literal["top", "bottom", "left", "right", "topleft", "topright", "bottomleft", "bottomright"]):
        positions = {
            "top": 1,
            "bottom": 2,
            "left": 4,
            "right": 8,
            "topleft": 5,
            "topright": 9,
            "bottomleft": 6,
            "bottomright": 10
        }
        return positions.get(position, 0)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.drag_position = event.globalPos()
            event.accept()

    def mouseMoveEvent(self, event: QMouseEvent):
        # todo: Fix resizing from corners
        if event.buttons() == Qt.LeftButton:
            border_size = 0
            exceding_width, exceding_height = False, False
            new_pos = event.globalPos()
            difference = self.drag_position - new_pos
            geo = self.main_window.frameGeometry()
            # 1111
            # 8421
            x, y, w, h = geo.topLeft().x(), geo.topLeft().y(), geo.width(), geo.height()

            # Top
            if 1 & self.position:
                new_height = geo.height() + difference.y()
                exceding_height = self.exceedingMinimumHeight(new_height)

                if exceding_height:
                    difference.setY(self.main_window.minimumHeight() - geo.height())
                    new_height = self.main_window.minimumHeight()

                y = geo.topLeft().y() - difference.y() - border_size
                h = new_height + border_size

            # Bottom
            elif 2 & self.position:
                new_height = geo.height() - difference.y()
                exceding_height = self.exceedingMinimumHeight(new_height)

                if exceding_height:
                    new_height = self.main_window.minimumHeight()

                h = new_height + border_size

            # Left
            if 4 & self.position:
                new_width = geo.width() + difference.x()
                exceding_width = self.exceedingMinimumWidth(new_width)

                if exceding_width:
                    difference.setX(self.main_window.minimumWidth() - geo.width())
                    new_width = self.main_window.minimumWidth()

                x = geo.topLeft().x() - difference.x() - border_size
                w = new_width + border_size

            # Right
            elif 8 & self.position:
                new_width = geo.width() - difference.x()
                exceding_width = self.exceedingMinimumWidth(new_width)

                if exceding_width:
                    new_width = self.main_window.minimumWidth()

                w = new_width + border_size

            self.main_window.setGeometry(x, y, w, h)

            self.drag_position = self.checkPositionValidity(new_pos, (exceding_width, exceding_height))
            event.accept()

    def checkPositionValidity(self, new_pos, exceding: tuple[bool, bool]):
        if not (exceding[0] or exceding[1]):
            return new_pos
        geo = self.main_window.frameGeometry()
        ew, eh = exceding
        x, y = 0, 0
        if ew:
            if 4 & self.position:
                x = geo.left()
            else:
                x = geo.right()
        if eh:
            if 1 & self.position:
                y = geo.top()
            else:
                y = geo.bottom()
        return QPoint(x if ew else new_pos.x(), y if eh else new_pos.y())

    def exceedingMinimumWidth(self, new_width):
        min_size = self.main_window.minimumSize()
        return new_width < min_size.width()

    def exceedingMinimumHeight(self, new_height):
        min_size = self.main_window.minimumSize()
        return new_height < min_size.height()

    def paintEvent(self, a0):
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(0, 0, 0, 1))


def makeResizingLayout(parent: QWidget):
    layout: QGridLayout = QGridLayout(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.setSizeConstraint(QLayout.SetNoConstraint)
    centralWidget = QWidget(parent)
    w = lambda pos, r, c: layout.addWidget(DraggableFrame(parent, pos), r, c)
    w("topleft", 0, 0), w("top", 0, 1), w("topright", 0, 2)
    w("left", 1, 0), layout.addWidget(centralWidget, 1, 1), w("right", 1, 2)
    w("bottomleft", 2, 0), w("bottom", 2, 1), w("bottomright", 2, 2)
    parent.setLayout(layout)
    return centralWidget


def colorize_svg(svg_path: str, color: str, size=(32, 32)) -> QIcon:
    pixmap = QPixmap(*size)
    pixmap.fill(QColor("transparent"))

    renderer = QSvgRenderer(svg_path)
    painter = QPainter(pixmap)
    renderer.render(painter)
    painter.setCompositionMode(QPainter.CompositionMode.CompositionMode_SourceIn)
    painter.fillRect(pixmap.rect(), QColor(color))
    painter.end()

    return QIcon(pixmap)


