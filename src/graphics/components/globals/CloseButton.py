from PyQt5.QtCore import pyqtSignal, QSize
from PyQt5.QtGui import QMouseEvent, QIcon
from PyQt5.QtWidgets import QPushButton, QMainWindow, QSizePolicy

from src.tools.Tools import find_path
from src.tools.Variables import Variable


class CloseButton(QPushButton):
    def __init__(self, parent, mainwindow: QMainWindow = None, tool: bool = True):
        super().__init__(parent)
        self.___tool = tool
        self.setIcon(QIcon(find_path("close.png")))
        self.setIconSize(QSize(20, 20))
        self.setObjectName("Close")
        self.setFixedHeight(34)
        self.setSizePolicy(QSizePolicy.MinimumExpanding, QSizePolicy.Minimum)

        self.___event_enabled = True
        self.___main_window = mainwindow if mainwindow is not None else parent
        self.___signals: list[Variable] = []

    def setEventEnabled(self, is_it: bool):
        self.___event_enabled = is_it

    def mousePressEvent(self, e: QMouseEvent):
        if not self.___event_enabled:
            e.ignore()
            return
        if self.___tool:
            self.___main_window.deleteLater()
        else:
            self.___main_window.close()
        for i in self.___signals:
            i.setValue(True)

    def addSignal(self, signal: Variable):
        if not signal.getType() is bool:
            raise TypeError("Variable type must be boolean...")
        self.___signals.append(signal)