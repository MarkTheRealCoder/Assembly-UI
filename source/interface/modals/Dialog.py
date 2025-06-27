from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QPalette
from PyQt5.QtWidgets import QLabel, QVBoxLayout, QSizePolicy, QLineEdit

from source.interface.shared import createLayout


class BoxGraphics(QLineEdit):
    def __init__(self, parent, prompt: str):
        super().__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setReadOnly(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setPlaceholderText(prompt)


class Box(BoxGraphics):
    def __init__(self, parent, prompt: str, action: callable):
        super().__init__(parent, prompt)

        if not callable(action):
            raise TypeError("The action must be a callable function")
        self.___action: callable = action

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            if not self.___action(self.text()):
                self.setText("")
                self.parent().log("Action failed, try again.")
            else:
                self.clearFocus()
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.parent().focus.emit("close")

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.text():
            self.palette().setColor(QPalette.PlaceholderText, Qt.GlobalColor.yellow)


class Title(QLabel):
    def __init__(self, parent, title: str):
        super().__init__(parent)

        self.setObjectName("Title")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(title)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(30)


class Dialog(QLabel):
    focus = pyqtSignal(str)

    def __init__(self, parent, title: str, prompt: str, action: callable):
        super().__init__(parent)
        self.___title = title

        self.configurations(title, prompt, action)
        self.focus.connect(self.onFocusLose)

        self.show()
        self.activateWindow()
        self.setFocus()

    def configurations(self, title: str, prompt: str, action: callable):
        self.setObjectName("Dialog")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setFixedSize(300, 150)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)

        title = Title(self, title)
        box = Box(self, prompt, action)
        self.setFocusProxy(box)
        title.setFocusProxy(box)

        layout.addWidget(title)
        layout.addWidget(box)

        self.setLayout(layout)

    def log(self, message: str):
        label = self.layout().itemAt(0).widget()
        label.setText(f"{self.___title}: {message}")

    def onFocusLose(self):
        self.deleteLater()



