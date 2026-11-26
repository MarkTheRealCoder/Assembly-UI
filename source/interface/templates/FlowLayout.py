# Copyright (C) 2013 Riverbank Computing Limited.
# Copyright (C) 2022 The Qt Company Ltd.
# SPDX-License-Identifier: LicenseRef-Qt-Commercial OR BSD-3-Clause
from __future__ import annotations

"""PySide6 port of the widgets/layouts/flowlayout example from Qt v6.x"""

from PyQt5.QtCore import Qt, QMargins, QPoint, QRect, QSize
from PyQt5.QtWidgets import QLayout, QSizePolicy

class FlowLayout(QLayout):
    """Layout that places items left to right and wraps them to the next row."""
    def __init__(self, parent=None):
        super().__init__(parent)

        if parent is not None:
            self.setContentsMargins(QMargins(0, 0, 0, 0))

        self._item_list = []

    def __del__(self):
        item = self.takeAt(0)
        while item:
            item = self.takeAt(0)

    def addItem(self, item):
        self._item_list.append(item)

    def count(self):
        return len(self._item_list)

    def itemAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list[index]

        return None

    def takeAt(self, index):
        if 0 <= index < len(self._item_list):
            return self._item_list.pop(index)

        return None

    def expandingDirections(self):
        return Qt.Orientation(0)

    def hasHeightForWidth(self):
        return True

    def heightForWidth(self, width):
        margins = self.contentsMargins()
        height = self._do_layout(QRect(0, 0, width - margins.left() - margins.right(), 0), True)
        return height + margins.top() + margins.bottom()

    def setGeometry(self, rect):
        super(FlowLayout, self).setGeometry(rect)
        self._do_layout(rect, False)

    def sizeHint(self):
        return self.minimumSize()

    def minimumSize(self):
        size = QSize()

        for item in self._item_list:
            size = size.expandedTo(item.minimumSize())

        size += QSize(2 * self.contentsMargins().top(), 2 * self.contentsMargins().top())
        return size

    @staticmethod
    def _fitted_size(item, width: int) -> QSize:
        """ Size of the item at most as wide as the layout, taller if its content wraps """
        hint = item.sizeHint()
        if width <= 0 or hint.width() <= width:
            return hint
        height = item.heightForWidth(width) if item.hasHeightForWidth() else -1
        return QSize(width, max(height, hint.height()) if height >= 0 else hint.height())

    def _do_layout(self, rect, test_only):
        x = rect.x()
        y = rect.y()
        line_height = 0
        spacing = self.spacing()

        for item in self._item_list:
            style = item.widget().style()
            layout_spacing_x = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Horizontal
            )
            layout_spacing_y = style.layoutSpacing(
                QSizePolicy.ControlType.PushButton, QSizePolicy.ControlType.PushButton,
                Qt.Orientation.Vertical
            )
            space_x = spacing + layout_spacing_x
            space_y = spacing + layout_spacing_y
            # An item wider than the layout is narrowed to its width, so it wraps its text instead of leaving the box.
            size = self._fitted_size(item, rect.width())
            next_x = x + size.width() + space_x
            if next_x - space_x > rect.right() + 1 and line_height > 0:
                x = rect.x()
                y = y + line_height + space_y
                next_x = x + size.width() + space_x
                line_height = 0

            if not test_only:
                item.setGeometry(QRect(QPoint(x, y), size))

            x = next_x
            line_height = max(line_height, size.height())

        return y + line_height - rect.y()