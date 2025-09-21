from typing import Literal

from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy, QLayout

from source.filesystem.documents import FT, Document
from source.interface.debugger.memorydisplay import Segment
from source.interface.shared import Settings


class MemoryGraphics(QLabel):
    def __init__(self, parent):
        super(QLabel, self).__init__(parent=parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setMinimumWidth(100)
        self.setObjectName("Memory")
        layout = QGridLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(7)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        self.setLayout(layout)


class MemoryLogic(MemoryGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self.___widgets: dict[str: Segment] = {
            "CONSTANTS": None,
            "VARIABLES": None,
            "SECT_DATA": None,
            "SECT_BSS": None,
            "STACK": None,
            "REGISTERS": None
        }

    def buildLayout(self, layout: QGridLayout, segments: list[str]) -> None:
        ijvm = len(segments) == 3
        for indx, widget in enumerate([self.___widgets.get(i) for i in segments]):
            row = 0
            if indx != 0:
                row = indx // 2
            col = indx % 2
            if not ijvm or indx != 2:
                layout.addWidget(widget, row, col, 1, 1)
            else:
                layout.addWidget(widget, row, col, 1, 2)

    def updateWidgets(self, segments: list[str], layout: QGridLayout) -> None:
        for i in self.___widgets.keys():
            oldwidget: QWidget = self.___widgets.get(i)
            if oldwidget is not None:
                layout.removeWidget(oldwidget)
                oldwidget.deleteLater()
                self.___widgets[i] = None
        for i in segments:
            self.___widgets[i] = Segment(self, i)

    def addFragment(self, target: Literal["CONSTANTS", "VARIABLES", "SECT_DATA", "SECT_BSS", "STACK", "REGISTERS"], _k: str, *args, _sk: str = None):
        m: Segment = self.___widgets.get(target)
        if m is not None:
            m.addFragment(_k, *args, _sk=_sk)
            self.update()


class Memory(MemoryLogic):
    def __init__(self, mwt: QWidget):
        super().__init__(parent=mwt)
        QTimer.singleShot(5000, lambda: add_mock_fragments(self))
        Settings.addNotificationGroup("editor/current", self.load_scopes)

    def load_scopes(self):
        if doc := Settings.get("editor/current", None):
            doctype = Document(doc).getExtension()
            doctype = FT.findByExt(doctype)

            if doctype == FT.F8088:
                segments: list[str] = ["SECT_DATA", "SECT_BSS", "STACK", "REGISTERS"]
            else:
                segments: list[str] = ["CONSTANTS", "VARIABLES", "STACK"]

            layout = self.layout()

            self.updateWidgets(segments, layout)
            self.buildLayout(layout, segments)
            self.setLayout(layout)
            self.update()


def add_mock_fragments(memory: Memory):
    """
    Adds mock fragments to the memory display for testing purposes.
    This function is called after the memory display is initialized.
    """
    memory.addFragment("CONSTANTS", "CONST1", "Value1")
    memory.addFragment("VARIABLES", "VAR1", "Value2")
    memory.addFragment("STACK", "STACK1", "Value3")


"""
DECL [CONST/VAR/REG] name
SAVE value IN [CONST/VAR/REG] name
PUSH [value/CONST/VAR/REG]
POP
AND
CHANGECONTEXT name (IJVM only)
ROLLBACK (HIDDEN)
"""


