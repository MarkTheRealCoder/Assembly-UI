from typing import Union

from PyQt5.QtCore import QObject, QEvent, Qt
from PyQt5.QtWidgets import QLabel, QSizePolicy, QHBoxLayout, QLayout, QApplication

from source.interface.debugger.memorydisplay.FragmentLabel import FragmentLabel


class FragmentGraphics(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setObjectName("Fragment")

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.setLayout(layout)


class FragmentLogic(FragmentGraphics):
    def __init__(self, parent, _k: str, *args, _sk: str = None):
        super().__init__(parent)
        self.___key: str = str(_k) if not isinstance(_k, str) else _k
        self.___secondary_key = str(_sk) if not isinstance(_sk, str) else _sk
        self.___args: tuple = args
        self.___hover = ""

        self.setGraphics()

    def setGraphics(self):
        layout: QHBoxLayout = self.layout() # noqas
        layout.addWidget(FragmentLabel(self, self.___key, True), 2)
        for i in self.___args:
            layout.addWidget(FragmentLabel(self, i), 1)
        layout.update()

    def getKey(self, _sk: bool = False) -> tuple[str, Union[str, None]]:
        return self.___key, self.___secondary_key

    def compare(self, _k: str, _sk: str):
        return _k == self.___key or (_sk is not None and self.___secondary_key == _sk)

    def __str__(self):
        return f"{self.___key}: {' '.join(self.___args)}"


class Fragment(QLabel):
    def __init__(self, parent, _k: str, *args, _sk: str = None):
        self.installEventFilter(self)

    def eventFilter(self, o: QObject, e: QEvent) -> bool:

        if hasattr(e, "button") and e.button() == Qt.LeftButton:

            if e.type() == QEvent.MouseButtonDblClick:
                clip = QApplication.clipboard()
                clip.setText(str(self), mode=clip.Clipboard)

        return super().eventFilter(o, e)





