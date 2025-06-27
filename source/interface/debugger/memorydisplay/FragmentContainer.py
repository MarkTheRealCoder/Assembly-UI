from itertools import takewhile

from PyQt5.QtCore import Qt, QObject
from PyQt5.QtWidgets import QLayout, QVBoxLayout, QSizePolicy, QFrame

from source.interface.debugger.memorydisplay.Fragment import Fragment


class FragmentContainerGraphics(QFrame):
    def __init__(self, parent, name):
        super(QFrame, self).__init__(parent)
        self.setObjectName(name)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout = QVBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSizeConstraint(QLayout.SetNoConstraint)
        layout.setAlignment(Qt.AlignTop)
        self.setLayout(layout)


class FragmentContainer(FragmentContainerGraphics):
    def __init__(self, parent, name):
        super().__init__(parent, name)

    def addFragment(self, widget: Fragment):
        layout: QVBoxLayout = self.layout() # noqas
        layout.addWidget(widget, 1)
        print(layout.count())

    def updateFragment(self, widget: Fragment):
        pass

    def delFragment(self, _ks: str, _sks: str = None) -> bool:
        layout: QVBoxLayout = self.layout() # noqas
        children = layout.children()
        fragments: list[Fragment] = list(filter(lambda f: f.compare(_ks, _sks), children))
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