from typing import Literal

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QWidget


class ColoredDrop(QWidget):
    def __init__(self, parent, radius: int, color: str, shape: Literal["square", "rounded-square", "circle"] = "square"):
        """
        Initializes a custom widget with a specified size, shape, and color. This widget
        inherits from a parent widget, sets a fixed size based on the radius provided,
        and customizes background attributes including style and palette settings.

        Parameters:
            parent: QWidget
                The parent widget for this custom widget.
            radius: int
                The radius used to calculate the size of the widget. The widget
                will have dimensions of radius * 2 by radius * 2.
            color: str
                The color used for the widget's background. Should be a valid
                color string recognized by QColor.
            shape: Literal["square", "rounded-square", "circle"], optional
                Determines the shape of the widget. Acceptable values are:
                'square' for a square-shaped widget, 'rounded-square' for a
                square with rounded corners, and 'circle' for a circular shape.
                Defaults to 'square'.
        """
        super().__init__(parent)
        self.setFixedSize(radius * 2, radius * 2)
        self.setAttribute(Qt.WA_StyledBackground, True)
        self.setStyleSheet(f"""
            background-color: {color};
            border-radius: {"0px" if shape == "square" else radius // 2 if shape == "rounded-square" else radius};
            margin: 0px;
            padding: 0px;
            border: none;
        """)
