import ctypes
from ctypes import cast
from ctypes.wintypes import LPRECT, MSG

import win32con
import win32gui
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAbstractButton, QWidget
from _ctypes import POINTER
from win32con import SW_MAXIMIZE, SW_RESTORE, SW_MINIMIZE

from source.interface.templates.window.effecthelper import WindowsEffectHelper
from source.interface.templates.window.types import getResizeBorderThickness, isMaximized, \
    NCCALCSIZE_PARAMS, Taskbar, trackNonClientLeave

WM_NCMOUSELEAVE = 0x02A2
_RESIZE_CORNER_EXTENT = 20
_RESIZE_HITS = (
    (win32con.HTTOPLEFT, win32con.HTTOP, win32con.HTTOPRIGHT),
    (win32con.HTLEFT, None, win32con.HTRIGHT),
    (win32con.HTBOTTOMLEFT, win32con.HTBOTTOM, win32con.HTBOTTOMRIGHT),
)


class BaseWindow(QWidget):
    """Frameless window that handles native hit testing for the resize edges and the Snap Layout maximize button."""
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windowEffect = None
        self.___border_width = 8
        # An empty rectangle: only windows with a maximize button replace it.
        self.MAXBUTTON_RECT = lambda: (0, 0, 0, 0)
        self._mouse_on_max_btn = False

    def setFrameless(self, hint=None, flags: list = []):
        if hint is None:
            hint = ['min', 'max', 'close']
        self._windowEffect = WindowsEffectHelper()

        # seems kinda pointless(though if you get rid of code below frame will still be seen), but if you don't add this, cursor won't properly work
        newFlags = self.windowFlags() | Qt.FramelessWindowHint
        for flag in flags:
            newFlags |= flag
        self.setWindowFlags(newFlags)

        # winId() on a tool window makes its siblings native, and they cover the owner's resize edges.
        self.create()
        self._windowEffect.setBasicEffect(self.effectiveWinId(), hint)

        self.windowHandle().screenChanged.connect(self._onScreenChanged)

    def _onScreenChanged(self):
        hWnd = int(self.windowHandle().winId())
        win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

    def _setMaxButtonHover(self, hovered: bool):
        from source.interface.titlebar.Maximize import MaximizeButton
        btn = self.findChild(MaximizeButton)
        if btn and btn.underMouse() != hovered:
            btn.setAttribute(Qt.WA_UnderMouse, hovered)
            btn.update()

    def nativeEvent(self, e, message):
        msg = MSG.from_address(message.__int__())
        if msg.hWnd:
            if msg.message == win32con.WM_NCHITTEST:
                global_pos = QCursor.pos()
                local_pos = self.mapFromGlobal(global_pos)
                x, y = local_pos.x(), local_pos.y()

                if QRect(*self.MAXBUTTON_RECT()).contains(QPoint(x, y)):
                    # todo fix button rect interaction after new window opening and closing
                    self._mouse_on_max_btn = True
                    # Comunichiamo a Windows che questo è il pulsante Maximize per attivare lo Snap Layout
                    return True, win32con.HTMAXBUTTON
                else:
                    if self._mouse_on_max_btn:
                        self._mouse_on_max_btn = False
                        self._setMaxButtonHover(False)

                if not isMaximized(msg.hWnd):
                    w, h = self.width(), self.height()
                    border = self.___border_width
                    if 0 <= x < w and 0 <= y < h and (
                            x < border or y < border or x >= w - border or y >= h - border):
                        column = 0 if x < _RESIZE_CORNER_EXTENT else 2 if x >= w - _RESIZE_CORNER_EXTENT else 1
                        row = 0 if y < _RESIZE_CORNER_EXTENT else 2 if y >= h - _RESIZE_CORNER_EXTENT else 1
                        # The rim overlaps the content here, so buttons keep their clicks outside the corners.
                        on_corner = column != 1 and row != 1
                        if on_corner or not isinstance(self.childAt(x, y), QAbstractButton):
                            return True, _RESIZE_HITS[row][column]

                return True, win32con.HTCLIENT

            # --- CORREZIONE HOVERING ---
            elif msg.message == win32con.WM_NCMOUSEMOVE:
                # Poiché Windows intercetta il mouse, forziamo l'effetto hover sul pulsante PyQt
                if msg.wParam == win32con.HTMAXBUTTON and self._mouse_on_max_btn:
                    self._setMaxButtonHover(True)
                    # Senza questa richiesta Windows non invia WM_NCMOUSELEAVE
                    trackNonClientLeave(msg.hWnd)

            # --- CORREZIONE USCITA DEL MOUSE DALLA FINESTRA ---
            elif msg.message == WM_NCMOUSELEAVE:
                if self._mouse_on_max_btn:
                    self._mouse_on_max_btn = False
                    self._setMaxButtonHover(False)

            # --- CORREZIONE CLICK (Pressione) ---
            elif msg.message == win32con.WM_NCLBUTTONDOWN:
                if msg.wParam == win32con.HTMAXBUTTON and self._mouse_on_max_btn:
                    # Intercettiamo il click PRIMA che Windows provi a disegnare il quadratino rosa nativo
                    from source.interface.titlebar.Maximize import MaximizeButton
                    btn = self.findChild(MaximizeButton)
                    if btn:
                        btn.on_press()
                        # Ritorniamo True per dire a Windows: "Gestito da me, non fare nulla (non disegnare robe)"
                    return True, 0

            # --- CORREZIONE RILASCIO CLICK ---
            elif msg.message == win32con.WM_NCLBUTTONUP:
                if msg.wParam == win32con.HTMAXBUTTON:
                    # Blocca l'evento nativo per evitare comportamenti anomali di Windows
                    return True, 0

            # --- RIMOZIONE PULSANTINO ROSA/NATIVO (DWM Paint) ---
            elif msg.message == 0x00AE:  # WM_NCUAHDRAWCAPTION (Messaggio non documentato di Windows per la topbar)
                return True, 0

            elif msg.message == win32con.WM_NCCALCSIZE:
                if msg.wParam:
                    rect = cast(msg.lParam, POINTER(NCCALCSIZE_PARAMS)).contents.rgrc[0]
                else:
                    rect = cast(msg.lParam, LPRECT).contents

                max_f = isMaximized(msg.hWnd)
                if max_f:
                    thickness = getResizeBorderThickness(msg.hWnd)
                    rect.top += thickness
                    rect.left += thickness
                    rect.right -= thickness
                    rect.bottom -= thickness

                if max_f and Taskbar.isAutoHide():
                    position = Taskbar.getPosition(msg.hWnd)
                    if position == Taskbar.TOP:
                        rect.top += Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.BOTTOM:
                        rect.bottom -= Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.LEFT:
                        rect.left += Taskbar.AUTO_HIDE_THICKNESS
                    elif position == Taskbar.RIGHT:
                        rect.right -= Taskbar.AUTO_HIDE_THICKNESS

                result = 0 if not msg.wParam else win32con.WVR_REDRAW
                return True, result

        return super().nativeEvent(e, message)


def _hwnd(widget: QWidget) -> int:
    return int(widget.winId())

def native_maximize(widget: QWidget):
    ctypes.windll.user32.ShowWindow(_hwnd(widget), SW_MAXIMIZE)

def native_restore(widget: QWidget):
    ctypes.windll.user32.ShowWindow(_hwnd(widget), SW_RESTORE)

def native_minimize(widget: QWidget):
    ctypes.windll.user32.ShowWindow(_hwnd(widget), SW_MINIMIZE)