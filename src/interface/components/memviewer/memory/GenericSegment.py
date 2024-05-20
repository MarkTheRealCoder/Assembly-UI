from itertools import takewhile
from typing import Union

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtGui import QClipboard
from PyQt5.QtWidgets import QScrollArea, QSizePolicy, QVBoxLayout, QLayout, QFrame

from src.interface.components.memviewer.memory.MemoryFragment import MemoryFragment


class ScrollWidget(QScrollArea):
    def __init__(self, parent, clipboard: QClipboard, title: str = None):
        super(QScrollArea, self).__init__(parent)
        self.___title: str = title
        self.setObjectName("GenericScroll")
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setWidgetResizable(True)
        self.___fc = FragmentContainer(self, f"{title}Scroll", clipboard)
        self.setWidget(self.___fc)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

    def getTitle(self):
        return self.___title

    def addFragment(self, _k: str, *args, _sk: str = None):
        self.___fc.addFragment(MemoryFragment(self.___fc, str(_k), *args, _sk=_sk))
        self.update()
        self.repaint()

    def delFragment(self, _k: Union[MemoryFragment, str]) -> bool:
        w: FragmentContainer = self.widget() # noqas

        _ks: str = None  # noqas
        _sks: str = None  # noqas

        if isinstance(_k, MemoryFragment):
            _ks, _sks = _k.getKey()
        else:
            _ks = _k

        return w.delFragment(_ks, _sks)

    def delAllFragments(self) -> bool:
        w: FragmentContainer = self.widget() # noqas
        return w.clearFragments()


class FragmentContainer(QFrame):
    def __init__(self, parent, name, clipboard):
        super().__init__(parent)
        self.___clipboard = clipboard
        self.setObjectName(name)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)

    def addFragment(self, widget: MemoryFragment):
        layout: QVBoxLayout = self.layout() # noqas
        layout.addWidget(widget, 1)
        print(layout.count())

    def delFragment(self, _ks: str, _sks: str = None) -> bool:
        layout: QVBoxLayout = self.layout() # noqas
        children = layout.children()
        fragments: list[MemoryFragment] = list(filter(lambda f: f.compare(_ks, _sks), children))
        any_frag = len(fragments) > 0
        for i in takewhile(lambda x: any_frag, fragments):
            layout.removeWidget(i)
            i.destroy(True, True)
        self.setLayout(layout)
        return any_frag

    def clearFragments(self):
        layout = self.layout()
        children = layout.children()

        def delete(child: QObject):
            nonlocal layout
            layout.removeWidget(child)
            child.deleteLater()

        map(delete, children)
        self.setLayout(layout)
        return layout.children() == []

    def getClipboard(self):
        return self.___clipboard

