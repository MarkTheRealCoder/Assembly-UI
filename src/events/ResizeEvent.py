from PyQt5.QtCore import Qt, QSize, QPoint, QEvent, QObject
from PyQt5.QtGui import QMouseEvent, QCursor
from PyQt5.QtWidgets import QMainWindow


class ResizeEvent(QObject):
    ___ACCEPTABLE_DEVIATION = 10

    def __init__(self, mw: QMainWindow):
        super().__init__()
        self.___mw = mw

        self.___minSize: QSize = self.___mw.minimumSize()
        self.___lmp: QPoint = None      # Last mouse position
        self.___lvy: int = None         # Last Valid Y
        self.___lvx: int = None         # Last Valid X
        self.___last_direction: str = ""

        self.___mw.mouseReleaseEvent = self.mouseReleaseEvent
        self.___mw.mousePressEvent = self.mousePressEvent

        self.___mouse_tracked: bool = False
        self.___mw.installEventFilter(self)
        self.___mw.setMouseTracking(True)

    def mouseReleaseEvent(self, event: QMouseEvent):
        self.___mouse_tracked = False
        self.___lvy = None
        self.___lvx = None

    def mousePressEvent(self, event: QMouseEvent):
        self.___mouse_tracked = True

    def eventFilter(self, obj, event: QMouseEvent):
        if event.type() in [QEvent.MouseMove, QEvent.HoverMove]:
            triggerPosition: QPoint = event.pos()
            current_widget = self.___mw.childAt(triggerPosition)
            ad = ResizeEvent.___ACCEPTABLE_DEVIATION
            x = self.___mw.width()
            y = self.___mw.height()
            combinations: dict[str: bool] = {
                "N": 0 <= triggerPosition.y() <= ad,
                "S": y >= triggerPosition.y() >= y - ad,
                "W": 0 <= triggerPosition.x() <= ad,
                "E": x >= triggerPosition.x() >= x - ad
            }

            direction = ""
            for i in combinations.keys():
                if combinations[i]:
                    direction += i

            cursor: dict[str: int] = {
                "N": Qt.SizeVerCursor,
                "S": Qt.SizeVerCursor,
                "W": Qt.SizeHorCursor,
                "E": Qt.SizeHorCursor,
                "NW": Qt.SizeFDiagCursor,
                "SE": Qt.SizeFDiagCursor,
                "SW": Qt.SizeBDiagCursor,
                "NE": Qt.SizeBDiagCursor
            }
            self.___mw.setCursor(QCursor(cursor.get(direction, Qt.ArrowCursor)))

            if hasattr(current_widget, "setEventEnabled"):
                current_widget.setEventEnabled(not any(combinations.values()))

            triggerPosition = self.___mw.mapToGlobal(triggerPosition)
            if self.___mouse_tracked:
                self.handle_movement(triggerPosition)
            else:
                self.___last_direction = direction
            self.___lmp = triggerPosition

        return super().eventFilter(obj, event)

    def handle_movement(self, gmouse_pos: QPoint):

        steps: dict[str: bool] = {}

        for i in self.___last_direction:
            if i == "N":
                steps["height"] = True
                steps["y"] = True
            elif i == "W":
                steps["width"] = True
                steps["x"] = True
            elif i == "S":
                steps["height"] = True
            elif i == "E":
                steps["width"] = True

        self.step(gmouse_pos, **steps)

    def step(self, gmouse_pos: QPoint, **kwargs):
        if len(kwargs) == 0:
            return

        size: QSize = self.___mw.size()
        min_size: QSize = self.___minSize

        window_corner: QPoint = self.___mw.pos()
        x, y = window_corner.x(), window_corner.y()

        lx, ly = self.___lmp.x(), self.___lmp.y()
        cx, cy = gmouse_pos.x(), gmouse_pos.y()

        width, height = size.width(), size.height()

        do_y = kwargs.get("y", False)
        do_x = kwargs.get("x", False)

        vlvy = self.___lvy is None or (self.___lvy > cy and do_y) or (self.___lvy < cy and not do_y)

        print("SUA ALTEZZA", height)

        if kwargs.get("height", False) and vlvy:
            print("COORDINATE", cy, ly, self.___lvy)
            _difference = cy - (ly if self.___lvy is None else self.___lvy)
            print("DIFFERENZA", _difference)
            tmpy = y
            if do_y:
                tmpy += _difference
                print("ADD DIFFERENCE TO Y", tmpy)
                _difference = -_difference
            height += _difference
            if height < min_size.height():
                height = min_size.height()
                self.___lvy = y + height if not do_y else y
            else:
                y = tmpy

        print("SUA ALTEZZA 2", height)
        self.___mw.move(x, y)
        self.___mw.resize(width, height)


"""
TODO:   COLORE TESTO
        COLORE HIGHLIGHT TESTO
        COLORE SFUMATURA BACKGROUND
        COLORE HIGHLIGHT BACKGROUND
        COLORE EXTRAS
"""