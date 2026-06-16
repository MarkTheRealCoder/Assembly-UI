import ctypes
from ctypes import cast
from ctypes.wintypes import LPRECT, MSG

import win32con
import win32gui
from PyQt5.QtCore import Qt, QRect, QPoint
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QWidget
from _ctypes import POINTER
from win32con import SW_MAXIMIZE, SW_RESTORE, SW_MINIMIZE

from source.interface.templates.window.effecthelper import WindowsEffectHelper
from source.interface.templates.window.types import getResizeBorderThickness, isMaximized, \
    NCCALCSIZE_PARAMS, Taskbar


class BaseWindow(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._windowEffect = None
        self.___border_width = 5
        self.MAXBUTTON_RECT = lambda: (100, 100, 10, 10)  # dummy value
        self._mouse_on_max_btn = False

    def setFrameless(self, hint=None, flags: list = []):
        if hint is None:
            hint = ['min', 'max', 'close']
        self._windowEffect = WindowsEffectHelper()

        # remove window border
        # seems kinda pointless(though if you get rid of code below frame will still be seen), but if you don't add this, cursor won't properly work
        newFlags = self.windowFlags() | Qt.FramelessWindowHint
        for flag in flags:
            newFlags |= flag
        self.setWindowFlags(newFlags)

        self._windowEffect.setBasicEffect(self.winId(), hint)

        self.windowHandle().screenChanged.connect(self._onScreenChanged)

    def _onScreenChanged(self):
        hWnd = int(self.windowHandle().winId())
        win32gui.SetWindowPos(hWnd, None, 0, 0, 0, 0, win32con.SWP_NOMOVE |
                              win32con.SWP_NOSIZE | win32con.SWP_FRAMECHANGED)

    def nativeEvent(self, e, message):
        msg = MSG.from_address(message.__int__())
        if msg.hWnd:
            if msg.message == win32con.WM_NCHITTEST:
                # 1. Coordinate locali tramite Qt
                global_pos = QCursor.pos()
                local_pos = self.mapFromGlobal(global_pos)
                x, y = local_pos.x(), local_pos.y()

                # Controllo se il mouse è nell'area del pulsante di massimizzazione
                if QRect(*self.MAXBUTTON_RECT()).contains(QPoint(x, y)):
                    # todo fix button rect interaction after new window opening and closing
                    self._mouse_on_max_btn = True
                    # Comunichiamo a Windows che questo è il pulsante Maximize per attivare lo Snap Layout
                    return True, win32con.HTMAXBUTTON
                else:
                    if self._mouse_on_max_btn:
                        self._mouse_on_max_btn = False
                        # Ripristina lo stato normale del pulsante Qt quando il mouse esce
                        from source.interface.titlebar.Maximize import MaximizeButton
                        btn = self.findChild(MaximizeButton)
                        if btn:
                            btn.setAttribute(Qt.WA_UnderMouse, False)
                            btn.update()

                # Gestione dei bordi di ridimensionamento (solo se non massimizzata)
                if not isMaximized(msg.hWnd):
                    w, h = self.width(), self.height()
                    left = x < self.___border_width
                    top = y < self.___border_width
                    right = x > w - self.___border_width
                    bottom = y > h - self.___border_width

                    v = None
                    if top and left:
                        v = win32con.HTTOPLEFT
                    elif top and right:
                        v = win32con.HTTOPRIGHT
                    elif bottom and left:
                        v = win32con.HTBOTTOMLEFT
                    elif bottom and right:
                        v = win32con.HTBOTTOMRIGHT
                    elif left:
                        v = win32con.HTLEFT
                    elif top:
                        v = win32con.HTTOP
                    elif right:
                        v = win32con.HTRIGHT
                    elif bottom:
                        v = win32con.HTBOTTOM

                    if v is not None:
                        return True, v

                return True, win32con.HTCLIENT

            # --- CORREZIONE HOVERING ---
            elif msg.message == win32con.WM_NCMOUSEMOVE:
                # Poiché Windows intercetta il mouse, forziamo l'effetto hover sul pulsante PyQt
                if msg.wParam == win32con.HTMAXBUTTON and self._mouse_on_max_btn:
                    from source.interface.titlebar.Maximize import MaximizeButton
                    btn = self.findChild(MaximizeButton)
                    if btn and not btn.underMouse():
                        btn.setAttribute(Qt.WA_UnderMouse, True)
                        btn.update()

            # --- CORREZIONE CLICK (Pressione) ---
            elif msg.message == win32con.WM_NCLBUTTONDOWN:
                if msg.wParam == win32con.HTMAXBUTTON and self._mouse_on_max_btn:
                    # Intercettiamo il click PRIMA che Windows provi a disegnare il quadratino rosa nativo
                    from source.interface.titlebar.Maximize import MaximizeButton
                    btn = self.findChild(MaximizeButton)
                    if btn:
                        # Simula il click sul pulsante Qt
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