from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy, QTabWidget, QFrame, QHBoxLayout

from source.interface.modals.settings.colors import ColorPicker
from source.interface.shared import createLayout


class TitledLine(QFrame):
    def __init__(self, title: str, parent=None):
        super().__init__(parent)

        # Layout for the title and line
        layout = createLayout(QHBoxLayout, self)
        layout.setSpacing(5)

        # Title label
        self.label = QLabel(title)
        layout.addWidget(self.label)

        # Line after the title
        self.line = QFrame()
        self.line.setFrameShape(QFrame.Shape.HLine)
        self.line.setFrameShadow(QFrame.Shadow.Plain)
        self.line.setMaximumHeight(1)
        layout.addWidget(self.line, 1)  # stretch=1 makes line expand
        layout.setAlignment(Qt.AlignVCenter | Qt.AlignLeft)

        # Allow stylesheet customization
        self.setObjectName("TitledLine")
        self.line.setObjectName("TitledLineLine")
        self.label.setObjectName("TitledLineLabel")


class SettingsWidgetGraphics(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setupUI()

    def setupUI(self):
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        main_widget: QTabWidget = QTabWidget(self)
        layout.addWidget(main_widget)
        main_widget.addTab(self.setupGeneralTab(main_widget), "General")
        main_widget.addTab(self.setupEditorTab(main_widget), "Editor")
        self.setLayout(layout)

    def setupGeneralTab(self, main_widget):
        widget = QWidget(main_widget)
        layout: QVBoxLayout = createLayout(QVBoxLayout, widget)
        layout.setAlignment(Qt.AlignTop)
        layout.addWidget(TitledLine("Accent Colors"))
        layout.addWidget(ColorPicker(widget, "Main Color"))
        layout.addSpacing(10)
        layout.addWidget(ColorPicker(widget, "Secondary Color"))
        widget.setLayout(layout)
        return widget

    def setupEditorTab(self, main_widget):
        widget = QWidget()
        layout = createLayout(QVBoxLayout, widget)
        label = QLabel("Editor Settings", widget)
        label.setAlignment(Qt.AlignCenter)
        layout.addWidget(label)
        return widget


class SettingsWidgetLogic(SettingsWidgetGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class SettingsWidget(SettingsWidgetLogic):
    def __init__(self, parent):
        super().__init__(parent)


