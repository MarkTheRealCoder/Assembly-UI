from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtWidgets import QFrame, QWidget, QSizePolicy, QHBoxLayout, QSpacerItem, QMenuBar, QPushButton

from source.interface.shared import createLayout
from source.interface.templates.CloseButton import CloseButton
from source.interface.titlebar.Files import FileMenu
from source.interface.titlebar.Icon import IconButton
from source.interface.titlebar.Maximize import MaximizeButton
from source.interface.titlebar.Minimize import MinimizeButton
from source.interface.titlebar.Title import Title
from source.interface.titlebar.UserHelp import HelpMenu
from source.platform import isMac, isLinux


class Toolbar(QFrame):

    def __init__(self, mwt: QWidget):
        super().__init__(mwt)
        self.setObjectName("Toolbar")
        self.setFixedHeight(35)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.addComponents()

    def addComponents(self):
        layout_clist = []

        mac_, linux_ = isMac(), isLinux()
        controls = self
        if mac_ or linux_:
            controls = QWidget(self)
            controls.setObjectName("WindowControls")
            controls.setProperty("platform", "mac" if mac_ else "linux")
            controls.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)

        properties = {"mac": mac_, "linux": linux_}
        cb = CloseButton(controls, properties=properties)
        mnb = MinimizeButton(controls, properties=properties)
        mxb = MaximizeButton(controls, properties=properties)
        title = Title(self)

        if mac_ or linux_:
            controls_layout = createLayout(QHBoxLayout, controls)
            margin = 12 if mac_ else 8
            controls_layout.setContentsMargins(margin, 0, margin, 0)
            controls_layout.setSpacing(8 if mac_ else 6)
            buttons = (cb, mnb, mxb) if mac_ else (mnb, mxb, cb)
            icon_size = QSize(0, 0) if mac_ else QSize(14, 14)
            for button in buttons:
                button.setIconSize(icon_size)
                controls_layout.addWidget(button, alignment=Qt.AlignVCenter)
            if mac_:
                controls.installEventFilter(self)

        if mac_:
            menubar: QMenuBar = self.window().menuBar()
            menubar.setNativeMenuBar(True)
            help_menu = HelpMenu.help_menu(menubar)
            help_menu.setTitle("Help")
            file_menu = FileMenu.file_menu(menubar)
            file_menu.setTitle("File")
            menubar.addMenu(file_menu)
            menubar.addMenu(help_menu)

            layout_clist.extend((controls, title))
        else:
            layout_clist.extend((IconButton(self), FileMenu(self), HelpMenu(self), title))
            if linux_:
                layout_clist.append(controls)
            else:
                layout_clist.extend((mnb, mxb, QSpacerItem(1, 15, QSizePolicy.Fixed, QSizePolicy.Fixed), cb))

        layout: QHBoxLayout = createLayout(QHBoxLayout, self)

        for i in layout_clist:
            if isinstance(i, QSpacerItem):
                layout.addSpacerItem(i)
            else:
                layout.addWidget(i)

        self.setLayout(layout)

    def eventFilter(self, watched, event):
        event_type = event.type()
        if event_type in (QEvent.Enter, QEvent.Leave) and watched.property("platform") == "mac":
            icon_size = QSize(10, 10) if event_type == QEvent.Enter else QSize(0, 0)
            for button in watched.findChildren(QPushButton, options=Qt.FindDirectChildrenOnly):
                button.setIconSize(icon_size)
        return super().eventFilter(watched, event)
