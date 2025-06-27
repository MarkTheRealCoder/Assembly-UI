from typing import Union

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QScrollArea, QSizePolicy, QLabel

from source.comms.Signals import DataBase as db
from source.interface.debugger.memorydisplay.Fragment import Fragment
from source.interface.debugger.memorydisplay.FragmentContainer import FragmentContainer


class SegmentScrollGraphics(QScrollArea):
    def __init__(self, parent, title: str):
        super(QScrollArea, self).__init__(parent)
        self.setObjectName("GenericScroll")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWidgetResizable(True)
        self.__fc = FragmentContainer(self, f"{title}Scroll")
        self.setWidget(self.__fc)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)


class SegmentScroll(SegmentScrollGraphics):
    def __init__(self, parent, title: str, contextChange: bool = False):
        super().__init__(parent, title)
        self.___title: str = title
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

    def getTitle(self):
        return self.___title

    def addFragment(self, _k: str, *args, _sk: str = None):
        self.__fc.addFragment(Fragment(self.__fc, str(_k), *args, _sk=_sk))
        self.update()
        self.repaint()

    def updateFragment(self, _k: str, *args, _sk: str = None):
        self.__fc.updateFragment(Fragment(self.__fc, str(_k), *args, _sk=_sk))
        self.update()
        self.repaint()

    def delFragment(self, _k: Union[Fragment, str]) -> bool:
        w: FragmentContainer = self.widget() # noqas

        _ks: str = None  # noqas
        _sks: str = None  # noqas

        if isinstance(_k, Fragment):
            _ks, _sks = _k.getKey()
        else:
            _ks = _k

        return w.delFragment(_ks, _sks)

    def delAllFragments(self) -> bool:
        w: FragmentContainer = self.widget() # noqas
        return w.clearFragments()

