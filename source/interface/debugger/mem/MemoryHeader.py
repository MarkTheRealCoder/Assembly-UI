from html import escape

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QSizePolicy

from source.interface.shared import createLayout
from source.interface.templates import FlowLayout


class MemoryHeaderGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MemoryHeader")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.program_counter = QLabel("""<span style="color: #6b6b6b;">pc</span> <span style="color: #1D9E75;">0</span><span style="color: #6b6b6b;"> / </span><span style="color: #1D9E75;">0x000000</span>""", self)
        self.instruction = QLabel("""<span style="color: #6b6b6b;">instr</span> <span style="color: #a0a0a0;">None</span>""", self)
        self.scope = QLabel("""<span style="color: #6b6b6b;">scope</span> <span style="color: #a0a0a0;">None</span>""", self)
        self.language = QLabel("""<span style="color: #6b6b6b;">lang</span> <span style="color: #a0a0a0;">None</span>""", self)
        self.setupLabels()

        layout: FlowLayout = createLayout(FlowLayout, self)
        layout.addWidget(self.program_counter)
        layout.addWidget(self.instruction)
        layout.addWidget(self.scope)
        layout.addWidget(self.language)
        self.setLayout(layout)

    def setupLabels(self):
        self.program_counter.setTextFormat(Qt.RichText)
        self.instruction.setTextFormat(Qt.RichText)
        self.scope.setTextFormat(Qt.RichText)
        self.language.setTextFormat(Qt.RichText)
        self.program_counter.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.instruction.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.scope.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        self.language.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)

    def updateProgramCounter(self, value: int):
        """ Show the program counter in decimal and hexadecimal """
        self.program_counter.setText(f"""<span style="color: #6b6b6b;">pc</span> <span style="color: #1D9E75;">{value}</span><span style="color: #6b6b6b;"> / </span><span style="color: #1D9E75;">0x{value:06X}</span>""")

    def updateInstruction(self, value: str):
        """ Show the current instruction """
        self.instruction.setText(f"""<span style="color: #6b6b6b;">instr</span> <span style="color: #a0a0a0;">{escape(str(value))}</span>""")

    def updateScope(self, value: str):
        """ Show the current scope """
        self.scope.setText(f"""<span style="color: #6b6b6b;">scope</span> <span style="color: #a0a0a0;">{escape(str(value))}</span>""")

    def updateLanguage(self, value: str):
        """ Show the language of the program """
        self.language.setText(f"""<span style="color: #6b6b6b;">lang</span> <span style="color: #a0a0a0;">{escape(str(value))}</span>""")


class MemoryHeaderLogic(MemoryHeaderGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class MemoryHeader(MemoryHeaderLogic):
    def __init__(self, parent):
        super().__init__(parent)
