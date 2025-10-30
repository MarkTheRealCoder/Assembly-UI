
from typing import Literal, Dict

from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtProperty
from PyQt5.QtGui import QCursor, QPainter, QPen, QBrush, QPolygon, QPalette, QColor, QBitmap
from PyQt5.QtWidgets import QLabel


class TooltipGraphics(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("Tooltip")
        self.arrow_size = 8  # Dimensione della freccia
        self.arrow_position = None  # Posizione della freccia: top, bottom, left, right
        self.arrow_offset = 0  # Offset dalla posizione centrale
        self._border_color = QColor(255, 255, 255)  # Colore del bordo di default

        self.setAttribute(Qt.WA_NoSystemBackground, True)
        self.setAttribute(Qt.WA_OpaquePaintEvent, False)

    def setSpecific(self, spec: str):
        self.setProperty(spec, True)
        self.style().unpolish(self)
        self.style().polish(self)
        self.update()

    def sizeHint(self):
        """Override sizeHint per includere lo spazio per la freccia"""
        base_hint = super().sizeHint()
        width = base_hint.width()
        height = base_hint.height()

        # Aggiungi spazio per la freccia
        if self.arrow_position in ["above", "below"]:
            height += self.arrow_size
        elif self.arrow_position in ["left", "right"]:
            width += self.arrow_size

        return base_hint.__class__(width, height)

    def get_content_rect(self):
        """Restituisce il rettangolo dove dovrebbe essere disegnato il contenuto del label"""
        rect = self.rect()

        if self.arrow_position == "above":
            rect.setBottom(rect.bottom() - self.arrow_size)
        elif self.arrow_position == "below":
            rect.setTop(rect.top() + self.arrow_size)
        elif self.arrow_position == "left":
            rect.setRight(rect.right() - self.arrow_size)
        elif self.arrow_position == "right":
            rect.setLeft(rect.left() + self.arrow_size)

        return rect

    def getBackgroundColor(self):#
        """Ottiene il colore di sfondo dagli stylesheets o dal palette"""
        return self.palette().color(QPalette.Window)

    @pyqtProperty(QColor)
    def borderColor(self):
        return self._border_color

    @borderColor.setter
    def borderColor(self, color):
        self._border_color = color

    def getBorderColor(self):
        """Ottiene il colore del bordo dagli stylesheets"""
        return self._border_color

    def getTextColor(self):
        """Ottiene il colore del testo dagli stylesheets o dal palette"""
        return self.palette().color(QPalette.WindowText)

    def _get_arrow_points(self):
        """Restituisce i punti della freccia"""
        arrow_points = QPolygon()
        widget_rect = self.get_content_rect()

        if self.arrow_position == "above":
            # Freccia che punta verso il basso (fuori dal widget, in alto)
            tip_x = widget_rect.center().x() + self.arrow_offset
            tip_y = widget_rect.y() + widget_rect.height() + self.arrow_size
            base_y = widget_rect.y() + widget_rect.height()

            arrow_points << QPoint(tip_x, tip_y)
            arrow_points << QPoint(tip_x - self.arrow_size, base_y)
            arrow_points << QPoint(tip_x + self.arrow_size, base_y)

        elif self.arrow_position == "below":
            # Freccia che punta verso l'alto (fuori dal widget, in basso)
            tip_x = widget_rect.center().x() + self.arrow_offset
            tip_y = widget_rect.y() - self.arrow_size
            base_y = widget_rect.y()

            arrow_points << QPoint(tip_x, tip_y)
            arrow_points << QPoint(tip_x - self.arrow_size, base_y)
            arrow_points << QPoint(tip_x + self.arrow_size, base_y)

        elif self.arrow_position == "left":
            # Freccia che punta verso destra (fuori dal widget, a sinistra)
            tip_x = widget_rect.x() + widget_rect.width() + self.arrow_size  # Punta al lato sinistro del widget
            tip_y = widget_rect.center().y() + self.arrow_offset
            base_x = widget_rect.x() + widget_rect.width()

            arrow_points << QPoint(tip_x, tip_y)
            arrow_points << QPoint(base_x, tip_y - self.arrow_size)
            arrow_points << QPoint(base_x, tip_y + self.arrow_size)

        elif self.arrow_position == "right":
            # Freccia che punta verso sinistra (fuori dal widget, a destra)
            tip_x = widget_rect.x() - self.arrow_size  # Punta al lato destro del widget
            tip_y = widget_rect.center().y() + self.arrow_offset
            base_x = widget_rect.x()

            arrow_points << QPoint(tip_x, tip_y)
            arrow_points << QPoint(base_x, tip_y - self.arrow_size)
            arrow_points << QPoint(base_x, tip_y + self.arrow_size)

        return arrow_points

    def _create_mask(self):
        """Crea la maschera del widget (solo bianco/nero per definire le aree visibili)"""
        bitmap = QBitmap(self.size())
        bitmap.fill(Qt.color0)  # Nero = trasparente

        mask_painter = QPainter(bitmap)
        mask_painter.setPen(QPen(Qt.color1))  # Bianco = visibile
        mask_painter.setBrush(QBrush(Qt.color1))

        # Disegna le aree che devono essere visibili
        content_rect = self.get_content_rect().adjusted(0, 0, 0, 0)
        mask_painter.fillRect(content_rect, Qt.color1)

        # Disegna la freccia
        arrow_points = self._get_arrow_points()
        mask_painter.drawPolygon(arrow_points)

        mask_painter.end()
        return bitmap

    def _update_mask(self):
        """Aggiorna la maschera del widget"""
        mask = self._create_mask()
        self.setMask(mask)

    def paintEvent(self, event):
        # QUESTO painter disegna SUL WIDGET, non sulla maschera!
        painter = QPainter(self)
        painter.setRenderHint(QPainter.SmoothPixmapTransform)

        # Ottieni i colori dal tema/stylesheet
        bg_color = self.getBackgroundColor() # QColor(37, 37, 38)  # #252526 -> in rgb = (37, 37, 38)
        text_color = self.getTextColor()
        border_color = self.getBorderColor() # QColor(255, 255, 255)

        # Disegna il background del contenuto
        content_rect = self.get_content_rect().adjusted(0, 0, -1, -1)
        painter.fillRect(content_rect, bg_color)

        # Disegna un bordo se necessario
        border_pen = QPen(border_color)
        painter.setPen(border_pen)
        painter.drawRect(content_rect)

        # Disegna il testo
        painter.setClipRect(content_rect)
        painter.setPen(text_color)
        painter.setFont(self.font())

        # Usa l'allineamento del label
        alignment = self.alignment()
        if alignment == 0:  # Se non è impostato alcun allineamento
            alignment = Qt.AlignHCenter | Qt.AlignVCenter

        # Aggiungi padding al testo
        text_rect = content_rect.adjusted(5, 2, -5, -2)
        painter.drawText(text_rect, alignment, self.text())

        # Reset clipping
        painter.setClipping(False)

        # Disegna la freccia con lo stesso colore del background
        painter.setPen(QPen(border_color))
        painter.setBrush(QBrush(border_color))
        arrow_points = self._get_arrow_points()
        painter.drawPolygon(arrow_points)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self._update_mask()

    def showEvent(self, event):
        super().showEvent(event)
        self._update_mask()

    def set_arrow_position(self, position: Literal["above", "below", "right", "left"]):
        """Imposta la posizione della freccia"""
        self.arrow_position = position
        self.adjustSize()  # Ricalcola la dimensione includendo la freccia
        self._update_mask()  # Aggiorna la maschera
        self.update()

    def set_arrow_size(self, size: int):
        """Imposta la dimensione della freccia"""
        self.arrow_size = size
        self.adjustSize()  # Ricalcola la dimensione includendo la freccia
        self._update_mask()  # Aggiorna la maschera
        self.update()

#    border: 1px solid var(---generic-highlight-text-color);
#    background-color: var(---generic-light-background-color);


class TooltipLogic(TooltipGraphics):
    def __init__(self, parent, text: str):
        super().__init__(parent)
        self.___default_following = "mouse"
        self.___default_position = ("below", "end")
        self.___semi_permanent = False
        self.___is_automatic = True
        self.setText(text)
        self.tooltip_timer = QTimer()
        self.tooltip_timer.setSingleShot(True)
        self.tooltip_timer.timeout.connect(self.showTooltip)

    def ___geometry_elements(self) -> Dict[Literal["x", "y", "width", "height"], int]:
        topleft_coords = (0, 0)
        width, height = 16, 16
        if self.___default_following == "mouse":
            cursor = QCursor()
            pos = cursor.pos()
            topleft_coords = pos.x(), pos.y()

            pixmap = cursor.pixmap()
            if not pixmap.isNull():
                width = pixmap.width()
                height = pixmap.height()

        elif self.___default_following == "widget":
            widget_rect = self.parent().rect()
            widget_pos = self.parent().mapToGlobal(widget_rect.topLeft())
            topleft_coords = widget_pos.x(), widget_pos.y()
            width = widget_rect.width()
            height = widget_rect.height()
        return {
            "x": topleft_coords[0],
            "y": topleft_coords[1],
            "width": width,
            "height": height
        }

    def _show(self):
        geo = self.___geometry_elements() # this x and y are the top-left of the element followed
        width, height = self.sizeHint().width(), self.sizeHint().height()
        final_pos: tuple[int, int] = (0, 0)
        position, moving = self.___default_position
        if position == "above":
            final_pos = (geo["x"] - (width // 2), geo["y"] - height)
            if moving == "center":
                final_pos = (final_pos[0] + (geo["width"] // 2), final_pos[1])
            elif moving == "end":
                final_pos = (final_pos[0] + geo["width"], final_pos[1])
        elif position == "below":
            final_pos = (geo["x"] - (width // 2), geo["y"] + geo["height"]) # + height
            if moving == "center":
                final_pos = (final_pos[0] + (geo["width"] // 2), final_pos[1])
            elif moving == "end":
                final_pos = (final_pos[0] + geo["width"], final_pos[1])
        elif position == "right":
            final_pos = (geo["x"] + geo["width"], geo["y"] - (height // 2)) # + width
            if moving == "center":
                final_pos = (final_pos[0], final_pos[1] + (geo["height"] // 2))
            elif moving == "end":
                final_pos = (final_pos[0], final_pos[1] + geo["height"])
        elif position == "left":
            final_pos = (geo["x"] - width, geo["y"] - (height // 2))
            if moving == "center":
                final_pos = (final_pos[0], final_pos[1] + (geo["height"] // 2))
            elif moving == "end":
                final_pos = (final_pos[0], final_pos[1] + geo["height"])
        self.move(*final_pos)
        self.show()

    def start_delay(self):
        self.tooltip_timer.start(1000)

    def stop_delay(self):
        self.tooltip_timer.stop()

    def setText(self, text: str):
        """Set the text of the tooltip, automatically detecting if it's HTML or plain text"""
        self.setTextFormat(Qt.RichText if self.___isHtmlContent(text) else Qt.PlainText)
        super().setText(text)
        self.adjustSize()

    def setFollowing(self, following: Literal["mouse", "widget"]):
        """Set whether the tooltip appears nearby the mouse or is fixed to the widget"""
        self.___default_following = following

    def setPosition(self, position: Literal["above", "below", "right", "left"], moving: Literal["center", "start", "end"] = "end"):
        """Set the position of the tooltip relative to the element followed"""
        self.___default_position = (position, moving)
        self.set_arrow_position(position)

    def setAutomatic(self, enable: bool):
        """Set whether the tooltip appears automatically on hover after a delay"""
        self.___is_automatic = enable

    def isAutomatic(self) -> bool:
        """Check if the tooltip is automatic"""
        return self.___is_automatic

    def setSemiPermanent(self, enable: bool):
        """Set whether the tooltip remains visible until explicitly dismissed"""
        self.___semi_permanent = enable

    def isSemiPermanent(self) -> bool:
        """Check if the tooltip is semi-permanent"""
        return self.___semi_permanent and self.___default_following == "widget"

    def showTooltip(self):
        """Show the tooltip"""
        self._show()

    def isShown(self) -> bool:
        """Check if the tooltip is currently shown"""
        return self.isVisible()

    def ___isHtmlContent(self, text: str) -> bool:
        """Rileva se il testo contiene HTML"""
        html_indicators = [
            '<b>', '</b>', '<i>', '</i>', '<u>', '</u>',
            '<br>', '<br/>', '<p>', '</p>', '<span>', '<div',
            '<h1>', '<h2>', '<h3>', '<h4>', '<h5>', '<h6>',
            '<ul>', '<ol>', '<li>', '<table>', '<tr>', '<td>',
            'style=', 'color:', 'font-'
        ]

        text_lower = text.lower()
        return any(indicator in text_lower for indicator in html_indicators)


class Tooltip(TooltipLogic):
    def __init__(self, parent, text: str):
        super().__init__(parent, text)
        self.hide()
        self.setAttribute(Qt.WA_TransparentForMouseEvents)
        self.setWindowFlags(Qt.ToolTip)
        self.__parent_enterEvent = parent.enterEvent
        self.__parent_leaveEvent = parent.leaveEvent
        self.__parent_mousePressEvent = parent.mousePressEvent
        parent.enterEvent = self._enterEvent
        parent.leaveEvent = self._leaveEvent
        parent.mousePressEvent = self._mousePressEvent

    def hideTooltip(self):
        """Hide the tooltip"""
        if not self.isSemiPermanent():
            self.hide()

    def _enterEvent(self, ev):
        if self.isAutomatic():
            self.start_delay()
        self.__parent_enterEvent(ev)

    def _leaveEvent(self, ev):
        self.stop_delay()
        self.hideTooltip()
        self.__parent_leaveEvent(ev)

    def _mousePressEvent(self, ev):
        self.stop_delay()
        self.hideTooltip()
        self.__parent_mousePressEvent(ev)

#    border: 1px solid var(---generic-highlight-text-color);
#    background-color: var(---generic-light-background-color);
