import threading
import time
from typing import Type, Literal

from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QGridLayout
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout, QSizePolicy, QLayout

from src.graphics.components.memorycomponents.GenericSegment import ScrollWidget
from src.graphics.components.memorycomponents.SegmentLabel import MemoryLabel
from src.tools.ClassMapping import getClass
from src.tools.Variables import DataBase as db
from src.tools.documents.FileTypes import FT


class MemoryOptions(QLabel):
    def __init__(self, mwt: QWidget):
        super(QLabel, self).__init__(parent=mwt)
        self.setObjectName("Options")


class Segment(QLabel):
    def __init__(self, parent, memoryrepr: Type, clipboard: QClipboard):
        super(QLabel, self).__init__(parent)

        self.setConfigurations()
        self.___memseg: ScrollWidget = memoryrepr(self, clipboard)
        self.___label: MemoryLabel = MemoryLabel(self, self.___memseg.getTitle())
        self.___clipboard = clipboard

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        layout.addWidget(self.___label, 0)
        layout.addWidget(self.___memseg, 3)
        self.setLayout(layout)
        self.update()

    def setConfigurations(self):
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

    def getLabel(self):
        return self.___label

    def getMemseg(self):
        return self.___memseg


class Memory(QLabel):

    def __init__(self, mwt: QWidget, clipboard: QClipboard):
        super(QLabel, self).__init__(parent=mwt)
        self.___widgets: dict[str: Segment] = {
            "CONSTANTS": None,
            "VARIABLES": None,
            "STACK": None,
            "REGISTERS": None
        }
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setObjectName("Memory")

        self.___clipboard = clipboard

        db.DOCTYPE.connect(self.load_scopes)
        db.NEW_WIDGET.connect(self.temp)

        timer = threading.Timer(5, test)
        timer.start()

    def load_scopes(self):
        doctype = db.DOCTYPE.getValue()

        segments: list[str] = ["CONSTANTS", "VARIABLES", "STACK"]
        if doctype == FT.F8088:
            segments.append("REGISTERS")

        layout = self.layout()
        if layout is None:
            layout = QGridLayout()
            layout.setContentsMargins(0, 0, 0, 0)
            layout.setSpacing(7)
            layout.setSizeConstraint(QLayout.SetNoConstraint)

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
                oldwidget.destroy(True, True)
                self.___widgets[i] = None
        for i in segments:
            self.___widgets[i] = Segment(self, getClass(i), self.___clipboard)

    def temp(self):
        self.addFragment(*(db.NEW_WIDGET.getValue()))

    def addFragment(self, trgt: Literal["CONSTANTS", "VARIABLES", "STACK", "REGISTERS"], _k: str, *args, _sk: str = None):
        m: Segment = self.___widgets.get(trgt)  # noqas
        if m is not None:
            v = m.getMemseg()
            v.addFragment(_k, *args, _sk=_sk)
            self.update()


def test():
    """
    db.DOCTYPE.setValue(FT.F8088)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.FIJVM)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.F8088)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.FIJVM)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.F8088)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.FIJVM)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.F8088)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.FIJVM)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.F8088)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.FIJVM)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.F8088)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.FIJVM)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.F8088)
    time.sleep(0.5)
    db.DOCTYPE.setValue(FT.FIJVM)
    time.sleep(0.5)
    """

    for i in range(5):
        time.sleep(0.5)
        db.NEW_WIDGET.setValue(("OBJREF", "0xFFFFF"))
        time.sleep(0.5)
        db.NEW_WIDGET.setValue(("SAVE", "0x65983"))
        time.sleep(0.5)
        db.NEW_WIDGET.setValue(("DOES", "0xAFFB1"))
        time.sleep(0.5)
        db.NEW_WIDGET.setValue(("TOEF", "0x9898"))


# TODO: Una volta creati i segmenti trovare un metodo rapido e ottimizzato di fornire la giusta istanza in base alla
#  chiave passata


"""
DECL [CONST/VAR/REG] name
SAVE value IN [CONST/VAR/REG] name
PUSH [value/CONST/VAR/REG]
POP
AND
CHANGECONTEXT name (IJVM only)
ROLLBACK (HIDDEN)
"""
