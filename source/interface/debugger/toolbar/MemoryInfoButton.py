from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon

from source.filesystem import find_path
from source.interface.templates import GenericButton, Tooltip


class MemoryInfoButtonGraphics(GenericButton):
    # The tooltip draws plain text, so the lines are split with newlines.
    ___TEXT = (
        "Memory values\n"
        "\n"
        "• Double-click a value to copy it to the clipboard.\n"
        "• Click the ASCII button of a value to show its character,\n"
        "   click it again to show the number.\n"
        "• Pick HEX, DEC or OCT to change the base of the numbers."
    )

    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("MemoryInfoButton")
        self.setIcon(self.rerenderIcon(QIcon(find_path("info.svg")), "#569CD6"))
        self.setIconSize(QSize(18, 18))

        # The button sits at the right end of the toolbar, so the tooltip opens on its left.
        self.tooltip = Tooltip(self, self.___TEXT)
        self.tooltip.setPosition("left", "end")
        self.tooltip.setFollowing("widget")
        # Shown on click, as the copy confirmation of the memory chunks, and hidden when the mouse leaves the button.
        self.tooltip.setAutomatic(False)
        self.tooltip.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)


class MemoryInfoButton(MemoryInfoButtonGraphics):
    """ Explains how to copy the memory values and how to switch their display """

    def __init__(self, parent):
        super().__init__(parent)
        self.clicked.connect(self.tooltip.showTooltip)
