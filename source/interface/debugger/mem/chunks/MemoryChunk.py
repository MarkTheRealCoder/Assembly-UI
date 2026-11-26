from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QFrame


class _MemoryChunk(QFrame):
    """ Base widget of a memory node, with the spawn and removal animations. """

    def __init__(self, parent):
        super().__init__(parent)
        self.___animation: QPropertyAnimation = None
        self.___first_spawn = True

    def ___flash(self, color, duration: int, end: float, curve) -> QPropertyAnimation:
        """ Replaces the running animation. The widget owns the new one, so both end together. """
        if self.___animation is not None:
            self.___animation.finished.disconnect()
            self.___animation.stop()
            self.___animation.deleteLater()

        effect = QGraphicsColorizeEffect(self)
        effect.setColor(color)
        effect.setStrength(0.8)
        self.setGraphicsEffect(effect)

        self.___animation = QPropertyAnimation(effect, b"strength", self)
        self.___animation.setDuration(duration)
        self.___animation.setStartValue(0.8)
        self.___animation.setEndValue(end)
        self.___animation.setEasingCurve(curve)
        return self.___animation

    def ___clear_effect(self):
        self.setGraphicsEffect(None)
        self.___animation = None

    def ___green_flash(self):
        animation = self.___flash(Qt.green, 2000, 0.0, QEasingCurve.OutCubic)
        animation.finished.connect(self.___clear_effect)
        animation.start()

    def ___white_flash(self):
        animation = self.___flash(Qt.white, 800, 0.0, QEasingCurve.OutCubic)
        animation.finished.connect(self.___clear_effect)
        animation.start()

    def ___blue_flash(self):
        animation = self.___flash(Qt.blue, 2000, 0.0, QEasingCurve.OutCubic)
        animation.finished.connect(self.___clear_effect)
        animation.start()

    def ___red_flash(self):
        animation = self.___flash(Qt.red, 1500, 0.05, QEasingCurve.Linear)
        animation.finished.connect(self.deleteLater)
        animation.start()
        return animation.finished

    def showEvent(self, event):
        super().showEvent(event)
        if self.___first_spawn:
            self.___first_spawn = False
            self.___green_flash()

    def updated(self):
        self.___blue_flash()

    def highlighted(self):
        """ Short white flash, for example after the user copied the chunk """
        self.___white_flash()

    def rm(self):
        """ Starts the removal animation. Qt removes the widget from its layout when it is deleted. """
        return self.___red_flash()
