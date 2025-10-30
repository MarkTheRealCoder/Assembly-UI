from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QSizePolicy, QLabel

from source.comms.Signals import DataBase as db
from source.interface.debugger_old.memorydisplay.Fragment import Fragment
from source.interface.debugger_old.memorydisplay.FragmentContainer import FragmentContainer


class SegmentScrollGraphics(QScrollArea):
    def __init__(self, parent, title: str):
        super(QScrollArea, self).__init__(parent)
        self.setObjectName("GenericScroll")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWidgetResizable(True)
        self.fc = FragmentContainer(self, f"{title}Scroll")
        self.setWidget(self.fc)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


class SegmentScrollLogic(SegmentScrollGraphics):
    def __init__(self, parent, title: str):
        super().__init__(parent, title)
        self.___title: str = title

    def getTitle(self):
        return self.___title

    def delFragment(self, _k: Union[Fragment, str]) -> bool:
        w: FragmentContainer = self.widget()

        _ks: str = None
        _sks: str = None

        if isinstance(_k, Fragment):
            _ks, _sks = _k.getKey()
        else:
            _ks = _k

        return w.delFragment(_ks, _sks)

    def delAllFragments(self) -> bool:
        w: FragmentContainer = self.widget()
        return w.clearFragments()


class SegmentScroll(SegmentScrollLogic):
    def __init__(self, parent, title: str, contextChange: bool = False):
        super().__init__(parent, title)
        if contextChange:
            db.METHOD.connect(self.changeContext)

    def changeContext(self):
        content = db.METHOD.getValue()
        label: QLabel = self.parent().getLabel()
        if content != "":
            label.setText(f"{self.getTitle()} - {content}")
        else:
            label.setText(self.getTitle())
        label.update()

    def addFragment(self, _k: str, *args, _sk: str = None):
        self.fc.addFragment(Fragment(self.fc, str(_k), *args, _sk=_sk))
        self.update()
        self.repaint()

    def updateFragment(self, _k: str, *args, _sk: str = None):
        self.fc.updateFragment(Fragment(self.fc, str(_k), *args, _sk=_sk))
        self.update()
        self.repaint()

