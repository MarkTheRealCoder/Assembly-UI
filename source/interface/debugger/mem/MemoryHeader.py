from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QFrame, QLabel, QSizePolicy

from source.interface.shared import createLayout
from source.interface.templates import FlowLayout


class MemoryHeaderGraphics(QFrame):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MemoryHeader")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # Additional UI setup can be done here
        self.program_counter = QLabel("""<span style="color: #6b6b6b;">pc</span> <span style="color: #1D9E75;">0x00000000</span>""", self)
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
        # self.program_counter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.instruction.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.scope.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        # self.language.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def updateProgramCounter(self, value: int):
        self.program_counter.setText(f"""<span style="color: #6b6b6b;">pc</span> <span style="color: #1D9E75;">0x{value:08X}</span>""")

    def updateInstruction(self, value: str):
        self.instruction.setText(f"""<span style="color: #6b6b6b;">instr</span> <span style="color: #a0a0a0;">{value}</span>""")

    def updateScope(self, value: str):
        self.scope.setText(f"""<span style="color: #6b6b6b;">scope</span> <span style="color: #a0a0a0;">{value}</span>""")

    def updateLanguage(self, value: str):
        self.language.setText(f"""<span style="color: #6b6b6b;">lang</span> <span style="color: #a0a0a0;">{value}</span>""")


class MemoryHeaderLogic(MemoryHeaderGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        # Implementation of memory header logic goes here


class MemoryHeader(MemoryHeaderLogic):
    def __init__(self, parent):
        super().__init__(parent)
        # Additional initialization for MemoryHeader