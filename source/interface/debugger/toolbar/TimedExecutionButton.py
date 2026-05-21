from PyQt5.QtCore import QSize, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QIcon, QColor
from PyQt5.QtWidgets import QGraphicsColorizeEffect

from source.filesystem import find_path
from source.interface.templates import GenericButton, Tooltip


class TimedExecutionButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setIcon(self.rerenderIcon(QIcon(find_path("metronome.svg")), "#1D9E75"))
        self.setIconSize(QSize(20, 20))
        self.setVisible(False)
        self.___active = False

        self.___pulse_effect = QGraphicsColorizeEffect(self)
        self.___pulse_effect.setColor(QColor("#CCCCCC"))
        self.___pulse_effect.setStrength(0)

        self.setGraphicsEffect(self.___pulse_effect)

        self.___anim = QPropertyAnimation(self.___pulse_effect, b"strength")
        self.___anim.setDuration(2000)
        self.___anim.setLoopCount(-1)
        self.___anim.setEasingCurve(QEasingCurve.SineCurve)
        self.___anim.setStartValue(0.5)
        self.___anim.setEndValue(0.0)
        self.___anim.stateChanged.connect(lambda state: self.___pulse_effect.setEnabled(state == QPropertyAnimation.Running))

        self.tooltip = Tooltip(self, "")
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)
        self.___tooltip_text = ""


    def _on_click_animation(self):
        self.___active = not self.___active
        if self.___active:
            self.___tooltip_text = self.tooltip.text()
            self.tooltip.setText("Click again to stop execution")
            self.___anim.start()
        else:
            self.tooltip.setText(self.___tooltip_text)
            self.___anim.stop()

    def enable(self):
        self.setVisible(True)

    def disable(self):
        self.setVisible(False)


class TimedExecutionButtonLogic(TimedExecutionButtonGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self.update_interval()

    def update_interval(self, interval=500):
        self.tooltip.setText(f"""Start automatic execution based on given interval\n(current interval {"500 ms" if interval == 500 else f"{interval / 1000} s"}).""")


class TimedExecutionButton(TimedExecutionButtonLogic):
    def __init__(self, parent):
        super().__init__(parent)
        self.clicked.connect(self._on_click_animation)