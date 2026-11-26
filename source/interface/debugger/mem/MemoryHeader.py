from html import escape

from PyQt5.QtCore import Qt, QVariantAnimation, QRectF, QPointF, QSize
from PyQt5.QtGui import QPainter, QPainterPath, QColor, QPen
from PyQt5.QtWidgets import QFrame, QLabel, QSizePolicy

from source.interface import createLayout
from source.interface.templates import FlowLayout


class HeaderLabel(QLabel):
    """ Label that keeps its text on one line while there is room, and wraps it only when the header gets narrower """

    ___MAX_WIDTH = 10000

    def __init__(self, text: str, parent):
        super().__init__(text, parent)
        self.___natural: tuple = None

    def sizeHint(self) -> QSize:
        # With word wrap on, QLabel guesses a narrow width and wraps short texts: use the width of the unwrapped text.
        if not self.wordWrap():
            return super().sizeHint()
        key = (self.text(), self.font().key(), self.contentsMargins())
        if self.___natural is None or self.___natural[0] != key:
            height = self.heightForWidth(self.___MAX_WIDTH)
            low, high = 1, self.___MAX_WIDTH
            while low < high:
                middle = (low + high) // 2
                if self.heightForWidth(middle) <= height:
                    high = middle
                else:
                    low = middle + 1
            self.___natural = (key, QSize(low, height))
        return self.___natural[1]


class MemoryHeaderGraphics(QFrame):
    # Must match the margin and the border radius of QFrame#MemoryHeader in style.qss.
    ___FRAME_MARGIN = 8
    ___FRAME_RADIUS = 8

    ___TRAIL_COLOR = QColor("#4FC3F7")
    ___TRAIL_LENGTH = 0.22
    ___TRAIL_SAMPLES = 48
    ___LAP_MS = 1800

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MemoryHeader")
        # The height follows the rows of the labels, so they never leave the box when the viewer gets narrow.
        policy = QSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        policy.setHeightForWidth(True)
        self.setSizePolicy(policy)
        self.program_counter = HeaderLabel("""<span style="color: #6b6b6b;">pc</span> <span style="color: #1D9E75;">0</span><span style="color: #6b6b6b;"> / </span><span style="color: #1D9E75;">0x000000</span>""", self)
        self.instruction = HeaderLabel("""<span style="color: #6b6b6b;">instr</span> <span style="color: #a0a0a0;">None</span>""", self)
        self.scope = HeaderLabel("""<span style="color: #6b6b6b;">scope</span> <span style="color: #a0a0a0;">None</span>""", self)
        self.language = HeaderLabel("""<span style="color: #6b6b6b;">lang</span> <span style="color: #a0a0a0;">None</span>""", self)
        self.setupLabels()

        layout: FlowLayout = createLayout(FlowLayout, self)
        layout.addWidget(self.program_counter)
        layout.addWidget(self.instruction)
        layout.addWidget(self.scope)
        layout.addWidget(self.language)
        self.setLayout(layout)

        self.___progress: float = 0.0
        self.___trail = QVariantAnimation(self)
        self.___trail.setStartValue(0.0)
        self.___trail.setEndValue(1.0)
        self.___trail.setDuration(self.___LAP_MS)
        self.___trail.setLoopCount(-1)
        self.___trail.valueChanged.connect(self.___advanceTrail)

    def setupLabels(self):
        self.program_counter.setTextFormat(Qt.RichText)
        self.instruction.setTextFormat(Qt.RichText)
        self.scope.setTextFormat(Qt.RichText)
        self.language.setTextFormat(Qt.RichText)
        self.program_counter.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.instruction.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.scope.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.language.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        # Labels wrap at spaces; a word longer than the box is cut at its edge instead of widening the box.
        for label in (self.program_counter, self.instruction, self.scope, self.language):
            label.setWordWrap(True)
            label.setMinimumWidth(1)

    def updateProgramCounter(self, value: int):
        """ Show the program counter in decimal and hexadecimal """
        self.program_counter.setText(f"""<span style="color: #6b6b6b;">pc</span> <span style="color: #1D9E75;">{value}</span><span style="color: #6b6b6b;"> / </span><span style="color: #1D9E75;">0x{value:06X}</span>""")
        self.___fitHeight()

    def updateInstruction(self, value: str, line: int = -1):
        """ Show the current instruction and its line in the source file """
        location = f"""<span style="color: #6b6b6b;"> @ line </span><span style="color: #1D9E75;">{line}</span>""" if line > 0 else ""
        self.instruction.setText(f"""<span style="color: #6b6b6b;">instr</span> <span style="color: #a0a0a0;">{escape(str(value))}</span>{location}""")
        self.___fitHeight()

    def updateScope(self, value: str):
        """ Show the current scope """
        self.scope.setText(f"""<span style="color: #6b6b6b;">scope</span> <span style="color: #a0a0a0;">{escape(str(value))}</span>""")
        self.___fitHeight()

    def updateLanguage(self, value: str):
        """ Show the language of the program """
        self.language.setText(f"""<span style="color: #6b6b6b;">lang</span> <span style="color: #a0a0a0;">{escape(str(value))}</span>""")
        self.___fitHeight()

    def ___fitHeight(self):
        """
        Keep the box at least as tall as its wrapped labels at the current width.
        The minimum reaches the main window, which then cannot get so short that the labels leave the box.
        """
        height = self.heightForWidth(self.width())
        if height > 0 and height != self.minimumHeight():
            self.setMinimumHeight(height)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if event.oldSize().width() != event.size().width():
            self.___fitHeight()

    def setWaiting(self, waiting: bool):
        """ Start or stop the light that runs around the border while the program waits for input """
        if waiting and self.___trail.state() != QVariantAnimation.Running:
            self.___trail.start()
        elif not waiting and self.___trail.state() == QVariantAnimation.Running:
            self.___trail.stop()
            self.update()

    def isWaiting(self) -> bool:
        return self.___trail.state() == QVariantAnimation.Running

    def ___advanceTrail(self, value):
        self.___progress = float(value)
        self.update()

    def paintEvent(self, event):
        super().paintEvent(event)
        if not self.isWaiting():
            return

        inset = self.___FRAME_MARGIN + 0.5
        rect = QRectF(self.rect()).adjusted(inset, inset, -inset, -inset)
        if rect.width() <= 0 or rect.height() <= 0:
            return
        path = QPainterPath()
        path.addRoundedRect(rect, self.___FRAME_RADIUS, self.___FRAME_RADIUS)

        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        color = QColor(self.___TRAIL_COLOR)

        # Draw the trail from its tail to its head, each segment brighter and wider than the previous one.
        previous: QPointF = None
        for sample in range(self.___TRAIL_SAMPLES + 1):
            fraction = sample / self.___TRAIL_SAMPLES
            point = path.pointAtPercent((self.___progress - self.___TRAIL_LENGTH * (1 - fraction)) % 1.0)
            if previous is not None:
                color.setAlphaF(fraction)
                painter.setPen(QPen(color, 1 + fraction * 1.5, Qt.SolidLine, Qt.RoundCap))
                painter.drawLine(previous, point)
            previous = point

        color.setAlphaF(1.0)
        painter.setPen(Qt.NoPen)
        painter.setBrush(color)
        painter.drawEllipse(previous, 3, 3)
        painter.end()


class MemoryHeaderLogic(MemoryHeaderGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class MemoryHeader(MemoryHeaderLogic):
    def __init__(self, parent):
        super().__init__(parent)
