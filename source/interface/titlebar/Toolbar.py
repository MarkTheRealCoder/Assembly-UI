from PyQt5.QtWidgets import QFrame, QWidget, QSizePolicy, QHBoxLayout, QSpacerItem, QMenuBar

from source.interface.shared import createLayout
from source.interface.templates.CloseButton import CloseButton
from source.interface.titlebar.Files import FileMenu
from source.interface.titlebar.Icon import IconButton
from source.interface.titlebar.Maximize import MaximizeButton
from source.interface.titlebar.Minimize import MinimizeButton
from source.interface.titlebar.Title import Title
from source.interface.titlebar.UserHelp import HelpMenu
from source.platform import isWindows, isMac, isLinux


class Toolbar(QFrame):

    def __init__(self, mwt: QWidget):
        super().__init__(mwt)
        self.setObjectName("Toolbar")
        self.setFixedHeight(35)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
        self.addComponents()

    def addComponents(self):
        layout_clist = []

        mac_, linux_, win_ = isMac(), isLinux(), isWindows()

        cb = CloseButton(self, properties={"mac": mac_, "linux": linux_})
        mnb = MinimizeButton(self, properties={"mac": mac_, "linux": linux_})
        mxb = MaximizeButton(self, properties={"mac": mac_, "linux": linux_})
        title = Title(self)

        if mac_:
            menubar: QMenuBar = self.window().menuBar()
            menubar.setNativeMenuBar(True)
            help_menu = HelpMenu.help_menu(menubar)
            help_menu.setTitle("Help")
            file_menu = FileMenu.file_menu(menubar)
            file_menu.setTitle("File")
            menubar.addMenu(file_menu)
            menubar.addMenu(help_menu)

            layout_clist.append(cb)
            layout_clist.append(mnb)
            layout_clist.append(mxb)
            layout_clist.append(title)
        else:
            layout_clist.append(IconButton(self))
            layout_clist.append(FileMenu(self))
            layout_clist.append(HelpMenu(self))
            layout_clist.append(title)
            layout_clist.append(mnb)
            layout_clist.append(mxb)
            layout_clist.append(QSpacerItem(1, 15, QSizePolicy.Fixed, QSizePolicy.Fixed))
            layout_clist.append(cb)

        layout: QHBoxLayout = createLayout(QHBoxLayout, self)

        for i in layout_clist:
            if isinstance(i, QSpacerItem):
                layout.addSpacerItem(i)
            else:
                layout.addWidget(i)

        self.setLayout(layout)