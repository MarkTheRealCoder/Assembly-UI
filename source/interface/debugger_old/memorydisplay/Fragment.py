from typing import Union

from PyQt5.QtCore import QObject, QEvent, Qt, pyqtProperty, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QLabel, QSizePolicy, QHBoxLayout, QLayout, QApplication

from source.interface.debugger_old.memorydisplay.FragmentLabel import FragmentLabel


class FragmentGraphics(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setFixedHeight(20)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setObjectName("Fragment")
        self._border_color = QColor(255, 255, 255, 0)  # Trasparente inizialmente
        self._animation = None


        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.setLayout(layout)

    @pyqtProperty(QColor)
    def borderColor(self):
        return self._border_color

    @borderColor.setter
    def borderColor(self, color):
        self._border_color = color
        self.setStyleSheet(f"""
            QLabel#Fragment {{
                border: 2px solid rgba({color.red()}, {color.green()}, {color.blue()}, {color.alpha()});
            }}
        """)

    def startHighlightAnimation(self, duration_ms=2000):
        """Avvia l'animazione del bordo per la durata specificata"""
        if self._animation:
            self._animation.stop()

        self._animation = QPropertyAnimation(self, b"borderColor")
        self._animation.setDuration(duration_ms)
        self._animation.setStartValue(QColor(0, 170, 255, 255))  # Blu con alpha pieno
        self._animation.setEndValue(QColor(0, 170, 255, 0))     # Blu trasparente
        self._animation.setEasingCurve(QEasingCurve.OutQuad)

        # Resetta il bordo alla fine dell'animazione
        self._animation.finished.connect(self.resetBorder)
        self._animation.start()

    def resetBorder(self):
        """Resetta il bordo allo stato normale"""
        self.setStyleSheet("")  # Torna agli stili CSS originali



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

    def modifyValues(self, _k: str, *args, _sk: str = None): # todo: complete refactoring
        self.___key = str(_k) if not isinstance(_k, str) else _k
        self.___secondary_key = str(_sk) if not isinstance(_sk, str) else _sk
        self.___args = args

        layout: QHBoxLayout = self.layout()

    def __str__(self):
        return f"{self.___key}: {' '.join(self.___args)}"


class Fragment(FragmentLogic):
    def __init__(self, parent, _k: str, *args, _sk: str = None):
        super().__init__(parent, _k, *args, _sk=_sk)
        self.installEventFilter(self)

    def eventFilter(self, o: QObject, e: QEvent) -> bool:

        if hasattr(e, "button") and e.button() == Qt.LeftButton:

            if e.type() == QEvent.MouseButtonDblClick:
                clip = QApplication.clipboard()
                clip.setText(str(self), mode=clip.Clipboard)

        return super().eventFilter(o, e)

    def modify(self, _k: str, *args, _sk: str = None):
        self.modifyValues(_k, *args, _sk=_sk)
        self.startHighlightAnimation()
        self.update()
        self.repaint()





