from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QHBoxLayout, QLabel, QPushButton, QVBoxLayout

from source.interface.modals.Dialog import Title
from source.interface.shared import createLayout
from source.platform import isMac


class PopupGraphics(QDialog):
    def __init__(self, parent, title: str, message: str, action: str):
        super().__init__(parent, Qt.Dialog | Qt.FramelessWindowHint)
        self.setObjectName("Popup")
        self.setWindowTitle(title)
        # Cocoa turns window-modal children into sheets.
        self.setWindowModality(Qt.ApplicationModal if isMac() else Qt.WindowModal)
        self.setMinimumWidth(360)

        label = QLabel(message, self)
        label.setObjectName("PopupMessage")
        label.setTextFormat(Qt.PlainText)
        label.setWordWrap(True)
        label.setMaximumWidth(420)

        self._cancel = QPushButton("Cancel", self)
        self._confirm = QPushButton(action, self)
        buttons = createLayout(QHBoxLayout, None)
        buttons.setSpacing(8)
        buttons.addStretch()
        for button in (self._cancel, self._confirm):
            button.setMinimumSize(92, 30)
            buttons.addWidget(button)

        layout = createLayout(QVBoxLayout, self)
        layout.setContentsMargins(16, 10, 16, 14)
        layout.setSpacing(10)
        layout.addWidget(Title(self, title))
        layout.addWidget(label)
        layout.addLayout(buttons)


class PopupLogic(PopupGraphics):
    def __init__(self, parent, title: str, message: str, action: str):
        super().__init__(parent, title, message, action)
        self._cancel.clicked.connect(self.reject)
        self._confirm.clicked.connect(self.accept)
        self._cancel.setDefault(True)
        self._cancel.setFocus()
        self._confirm.setAutoDefault(False)


class Popup(PopupLogic):
    @classmethod
    def ask(cls, parent, title: str, message: str, action: str) -> bool:
        popup = cls(parent, title, message, action)
        confirmed = popup.exec_() == QDialog.Accepted
        popup.deleteLater()
        return confirmed
