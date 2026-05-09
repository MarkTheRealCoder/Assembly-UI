from PyQt5.QtCore import QPropertyAnimation, QEasingCurve, Qt
from PyQt5.QtWidgets import QGraphicsColorizeEffect, QFrame


class _MemoryChunk(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.___spawn_effect = QGraphicsColorizeEffect(self)
        self.___spawn_effect.setColor(Qt.green)
        self.___spawn_effect.setStrength(0)
        self.___close_effect = QGraphicsColorizeEffect(self)
        self.___close_effect.setColor(Qt.red)
        self.___close_effect.setStrength(0)
        self.___first_spawn = True

    def ___green_flash(self):
        self.setGraphicsEffect(self.___spawn_effect)
        self.anim = QPropertyAnimation(self.___spawn_effect, b"strength")
        self.anim.setDuration(2000)
        self.anim.setStartValue(0.8)
        self.anim.setEndValue(0.0)
        self.anim.setEasingCurve(QEasingCurve.OutCubic)

        # Optional: Clean up the effect when done to save CPU
        self.anim.finished.connect(lambda: self.setGraphicsEffect(None))

        self.anim.start()

    def ___red_flash(self):
        self.setGraphicsEffect(self.___close_effect)
        self.anim2 = QPropertyAnimation(self.___close_effect, b"strength")
        self.anim2.setDuration(1500)
        self.anim2.setStartValue(0.8)
        self.anim2.setEndValue(0.05)
        self.anim2.setEasingCurve(QEasingCurve.Linear)

        # Optional: Clean up the effect when done to save CPU
        self.anim2.finished.connect(lambda: self.deleteLater())

        self.anim2.start()
        return self.anim2.finished

    def showEvent(self, event):
        super().showEvent(event)
        if self.___first_spawn:
            self.___first_spawn = False
            self.___green_flash()

    def rm(self):
        return self.___red_flash()
