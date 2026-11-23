from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QKeyEvent, QPalette
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QSizePolicy, QLineEdit

from source.interface.shared import createLayout

DIALOG_HEIGHT = 150


class BoxGraphics(QLineEdit):
    def __init__(self, parent, prompt: str):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setReadOnly(False)
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)
        self.setPlaceholderText(prompt)


class BoxLogic(BoxGraphics):
    def __init__(self, parent, prompt: str, action: callable):
        super().__init__(parent, prompt)
        if not callable(action):
            raise TypeError("The action must be a callable function")
        self._action: callable = action


class Box(BoxLogic):
    def __init__(self, parent, prompt: str, action: callable):
        super().__init__(parent, prompt, action)

    def keyPressEvent(self, event: QKeyEvent):
        if event.key() == Qt.Key.Key_Return:
            if not self._action(self.text()):
                self.selectAll()
                self.parent().showError()
            else:
                self.clearFocus()
        elif event.key() == Qt.Key.Key_Escape:
            # Release focus first: a focus-out during the parent's deletion cannot reach the signal.
            self.clearFocus()
            self.parent().focus.emit("close")
        else:
            super().keyPressEvent(event)

    def focusOutEvent(self, event):
        self.parent().focus.emit("close")

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.text():
            self.palette().setColor(QPalette.PlaceholderText, Qt.GlobalColor.yellow)


class TitleGraphics(QLabel):
    def __init__(self, parent, title: str):
        super().__init__(parent)
        self.setObjectName("Title")
        self.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setText(title)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setFixedHeight(30)


class TitleLogic(TitleGraphics):
    def __init__(self, parent, title: str):
        super().__init__(parent, title)


class Title(TitleLogic):
    def __init__(self, parent, title: str):
        super().__init__(parent, title)


class DialogGraphics(QLabel):
    focus = pyqtSignal(str)

    def __init__(self, parent, title: str, prompt: str, action: callable, error: str):
        super().__init__(parent)
        self._title = title
        self._error_message = error
        self.configurations(title, prompt, action)

    def configurations(self, title: str, prompt: str, action: callable):
        self.setObjectName("Dialog")
        self.setWindowModality(Qt.WindowModality.NonModal)
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint | Qt.Tool)
        self.setFixedSize(300, DIALOG_HEIGHT)

        layout: QVBoxLayout = createLayout(QVBoxLayout, self)

        title_widget = Title(self, title)
        box = Box(self, prompt, action)
        self.setFocusProxy(box)
        title_widget.setFocusProxy(box)

        self._error = QLabel(self)
        self._error.setObjectName("DialogError")
        self._error.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._error.setWordWrap(True)
        self._error.hide()
        self._box = box

        layout.addWidget(title_widget)
        layout.addWidget(box)
        layout.addWidget(self._error)

        self.setLayout(layout)


class DialogLogic(DialogGraphics):
    def __init__(self, parent, title: str, prompt: str, action: callable, error: str):
        super().__init__(parent, title, prompt, action, error)

    def showError(self):
        self._error.setText(self._error_message)
        self._error.ensurePolished()
        self._error.show()
        # The modal grows so that the error does not cover the name field.
        self.setFixedHeight(DIALOG_HEIGHT + self._error.heightForWidth(self.width()))

    def hideError(self):
        self._error.hide()
        self.setFixedHeight(DIALOG_HEIGHT)


class Dialog(DialogLogic):
    def __init__(self, parent, title: str, prompt: str, action: callable,
                 error: str = "Action failed, try again."):
        super().__init__(parent, title, prompt, action, error)
        self._box.textEdited.connect(self.hideError)
        self.focus.connect(self.onFocusLose)
        self.show()
        if not QApplication.platformName().startswith("wayland"):
            self.activateWindow()
        self.setFocus()

    def onFocusLose(self):
        self.deleteLater()



