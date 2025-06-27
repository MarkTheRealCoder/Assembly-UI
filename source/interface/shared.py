from PyQt5.QtWidgets import QWidget, QLayout


def createLayout(l: type, parent: QWidget):
    layout = l(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.setSizeConstraint(QLayout.SetNoConstraint)
    return layout