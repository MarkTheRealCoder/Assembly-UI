from PyQt5.QtWidgets import QLabel, QLayout, QVBoxLayout, QSizePolicy

from source.interface.debugger.memorydisplay.SegmentLabel import SegmentLabel
from source.interface.debugger.memorydisplay.SegmentScroll import SegmentScroll


class Segment(QLabel):
    def __init__(self, parent, name: str):
        super(QLabel, self).__init__(parent)

        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.___memseg: SegmentScroll = SegmentScroll(self, name.title())
        self.___label: SegmentLabel = SegmentLabel(self, self.___memseg.getTitle())

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

    def getMemseg(self):
        return self.___memseg