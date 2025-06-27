from typing import Literal

from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel, QWidget, QSizePolicy, QLayout

from source.comms import Database as db
from source.filesystem.documents import FT
from source.interface.debugger.memorydisplay import Segment


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


class Memory(MemoryGraphics):
    def __init__(self, mwt: QWidget):
        super().__init__(parent=mwt)
        self.___widgets: dict[str: Segment] = {
            "CONSTANTS": None,
            "VARIABLES": None,
            "STACK": None,
            "REGISTERS": None
        }

        db.DOCTYPE.connect(self.load_scopes)

    def load_scopes(self):
        doctype = db.DOCTYPE.getValue()

        segments: list[str] = ["CONSTANTS", "VARIABLES", "STACK"]
        if doctype == FT.F8088:
            segments.append("REGISTERS")

        layout = self.layout()

        self.updateWidgets(segments, layout)
        self.buildLayout(layout, segments)
        self.setLayout(layout)
        self.update()

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
            oldwidget: QWidget = self.___widgets.get(i) # noqas
            if oldwidget is not None:
                layout.removeWidget(oldwidget)
                oldwidget.deleteLater()
                self.___widgets[i] = None
        for i in segments:
            self.___widgets[i] = Segment(self, i)

    def addFragment(self, trgt: Literal["CONSTANTS", "VARIABLES", "STACK", "REGISTERS"], _k: str, *args, _sk: str = None):
        m: Segment = self.___widgets.get(trgt)  # noqas
        if m is not None:
            v = m.getMemseg()
            v.addFragment(_k, *args, _sk=_sk)
            self.update()


"""
DECL [CONST/VAR/REG] name
SAVE value IN [CONST/VAR/REG] name
PUSH [value/CONST/VAR/REG]
POP
AND
CHANGECONTEXT name (IJVM only)
ROLLBACK (HIDDEN)
"""


