from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QFrame, QLineEdit, QLabel, QHBoxLayout, QSpacerItem, QSizePolicy

from source.comms.events.FindShortcut import FindShortcutEvent
from source.comms.handlers import EventRegister
from source.filesystem import find_path
from source.interface.shared import createLayout
from source.interface.templates import GenericButton, Tooltip


class TextBox(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("FindTextBox")
        # Additional UI setup can be done here
        self.setPlaceholderText("Search...")


class OccurrenceCounter(QLabel):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("OccurrenceCounter")
        # Additional UI setup can be done here
        self.setText("0 results")


class GenericFindButton(GenericButton):
    def __init__(self, parent, icon_path: str, tooltip_text: str):
        super().__init__(parent)
        self.setObjectName("FinderButton")
        # Additional UI setup can be done here
        self.show_icon = self.rerenderIcon(QIcon(find_path(icon_path)), "#569CD6")
        self.setIcon(self.show_icon)
        self.setIconSize(QSize(15, 15))

        self.tooltip = Tooltip(self, tooltip_text)
        self.tooltip.setPosition("below", "center")
        self.tooltip.setFollowing("widget")
        self.tooltip.setAutomatic(True)

    def ___reloadStyle(self):
        self.style().unpolish(self)
        self.style().polish(self)

    def activeProtocol(self):
        self.setProperty("active", True)
        self.___reloadStyle()

    def inactiveProtocol(self):
        self.setProperty("active", False)
        self.___reloadStyle()


class FindWidgetGraphics(QFrame):
    def __init__(self, parent, _source_type: str):
        super().__init__(parent)
        self.setObjectName("FindWidget")
        # Additional UI setup can be done here
        self.setVisible(False)

        self._enable_regex = GenericFindButton(self, "regex.svg", "Enable Regex Search")
        self._text_box = TextBox(self)
        self._find_button = GenericFindButton(self, "search-find.svg", f"Search inside the {_source_type}.")

        self._occurrence_prev = GenericFindButton(self, "arrow-left.svg", "Previous Occurrence")
        self._occurrence_counter = OccurrenceCounter(self)
        self._occurrence_next = GenericFindButton(self, "arrow-right.svg", "Next Occurrence")

        self._close_button = GenericFindButton(self, "close.svg", "Close")

        layout: QHBoxLayout = createLayout(QHBoxLayout, self)
        layout.setSpacing(10)
        layout.addWidget(self._text_box)
        layout.addWidget(self._find_button)
        layout.addSpacerItem(QSpacerItem(10, 1, QSizePolicy.Minimum, QSizePolicy.Fixed))
        layout.addWidget(self._occurrence_prev)
        layout.addWidget(self._occurrence_counter)
        layout.addWidget(self._occurrence_next)
        layout.addSpacerItem(QSpacerItem(10, 1, QSizePolicy.Expanding, QSizePolicy.Fixed))
        layout.addWidget(self._close_button)


class FindWidgetLogic(FindWidgetGraphics):
    def __init__(self, parent, _source_type: str):
        super().__init__(parent, _source_type)
        # Implementation of find widget logic goes here
        self._source_type: str = _source_type
        self._visibility: bool = False
        self.___regex: bool = False
        self.___occurrencies: list = None
        self.___index: int = -1

    def toggle(self):
        self._visibility = not self._visibility
        self.setVisible(self._visibility)
        return self._visibility

    def toggleRegex(self):
        self.___regex = not self.___regex
        if self.___regex:
            self._enable_regex.activeProtocol()
        else:
            self._enable_regex.inactiveProtocol()

    def ___move_to_occurrence(self):
        pass

    def ___get_occurrencies(self):
        search_text: str = self._text_box.text()
        regex: bool = self.___regex
        return []

    def find(self):
        if occurrencies := self.___get_occurrencies():
            self.___occurrencies = occurrencies
            self._occurrence_counter.setText(f"{self.___index + 1} of {len(occurrencies)}")
        else:
            self.___occurrencies = None
            self._occurrence_counter.setText("0 results")

    def prevOccurrence(self):
        pass

    def nextOccurrence(self):
        pass

    def _hide(self):
        EventRegister.send(FindShortcutEvent(), self._source_type)



class FindWidget(FindWidgetLogic):
    def __init__(self, parent, _source_type: str):
        super().__init__(parent, _source_type)
        EventRegister.mregister(self, FindShortcutEvent, _source_type)

        self._find_button.clicked.connect(self.find)
        self._occurrence_prev.clicked.connect(self.prevOccurrence)
        self._occurrence_next.clicked.connect(self.nextOccurrence)
        self._close_button.clicked.connect(self._hide)

    def event(self, e):
        return super().event(e)

    def onFindShortcutEvent(self, event: FindShortcutEvent):
        if self.toggle():
            self._text_box.setFocus()
