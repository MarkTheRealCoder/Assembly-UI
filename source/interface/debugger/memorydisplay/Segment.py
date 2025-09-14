from typing import Union

from PyQt5.QtWidgets import QLabel, QLayout, QVBoxLayout, QSizePolicy

from source.interface.debugger.memorydisplay.Fragment import Fragment
from source.interface.debugger.memorydisplay.SegmentLabel import SegmentLabel
from source.interface.debugger.memorydisplay.SegmentScroll import SegmentScroll


class Segment(QLabel):
    def __init__(self, parent, name: str):
        super(QLabel, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        _name = str(name).title()
        self.___memseg: SegmentScroll = SegmentScroll(self, _name)
        self.___label: SegmentLabel = SegmentLabel(self, _name)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        layout.addWidget(self.___label, 1)
        layout.addWidget(self.___memseg, 5)
        self.setLayout(layout)
        self.update()

    def getLabel(self):
        return self.___label

    def changeContext(self):
        self.___memseg.changeContext()

    def getTitle(self):
        return self.___title

    def addFragment(self, _k: str, *args, _sk: str = None):
        self.___memseg.addFragment(_k, *args, _sk=_sk)

    def updateFragment(self, _k: str, *args, _sk: str = None):
        self.___memseg.updateFragment(_k, *args, _sk=_sk)

    def delFragment(self, _k: Union[Fragment, str]) -> bool:
        return self.___memseg.delFragment(_k)

    def delAllFragments(self) -> bool:
        return self.___memseg.delAllFragments()