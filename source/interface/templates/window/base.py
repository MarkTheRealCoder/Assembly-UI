import ctypes
from ctypes import cast
from ctypes.wintypes import LPRECT, MSG

import win32con
import win32gui
from PyQt5.QtCore import Qt
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
        # check if it is message from Windows OS
        if msg.hWnd:
            # update cursor shape to resize/resize feature
            # get WM_NCHITTEST message
            # more info - https://learn.microsoft.com/ko-kr/windows/win32/inputdev/wm-nchittest
            if msg.message == win32con.WM_NCHITTEST:
                if not isMaximized(msg.hWnd):
                    pos = QCursor.pos()
                    x = pos.x() - self.x()
                    y = pos.y() - self.y()

                    w, h = self.width(), self.height()

                    left = x < self.___border_width
                    top = y < self.___border_width
                    right = x > w - self.___border_width
                    bottom = y > h - self.___border_width

                    # to support snap layouts
                    # more info - https://learn.microsoft.com/en-us/windows/apps/desktop/modernize/apply-snap-layout-menu
                    # if win32gui.PtInRect((10, 10, 100, 100), (x, y)):
                    #     return True, win32con.HTMAXBUTTON
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
                    return True, v if v is not None else win32con.HTCLIENT

            # maximize/minimize/full screen feature
            # get WM_NCCALCSIZE message
            # more info - https://learn.microsoft.com/ko-kr/windows/win32/winmsg/wm-nccalcsize
            elif msg.message == win32con.WM_NCCALCSIZE:
                if msg.wParam:
                    rect = cast(msg.lParam, POINTER(NCCALCSIZE_PARAMS)).contents.rgrc[0]
                else:
                    rect = cast(msg.lParam, LPRECT).contents

                max_f = isMaximized(msg.hWnd)
                # adjust the size of window
                if max_f:
                    thickness = getResizeBorderThickness(msg.hWnd)
                    rect.top += thickness
                    rect.left += thickness
                    rect.right -= thickness
                    rect.bottom -= thickness

                # for auto-hide taskbar
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
            # elif msg.message == win32con.WM_STYLECHANGING:
            #     self.___resizable = not isMaximized(msg.hWnd)
        return super().nativeEvent(e, message)


def _hwnd(widget: QWidget) -> int:
    return int(widget.winId())

def native_maximize(widget: QWidget):
    ctypes.windll.user32.ShowWindow(_hwnd(widget), SW_MAXIMIZE)

def native_restore(widget: QWidget):
    ctypes.windll.user32.ShowWindow(_hwnd(widget), SW_RESTORE)

def native_minimize(widget: QWidget):
    ctypes.windll.user32.ShowWindow(_hwnd(widget), SW_MINIMIZE)