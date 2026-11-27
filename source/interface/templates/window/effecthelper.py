from ctypes import windll, c_int

import win32con
import win32gui
from _ctypes import Structure, byref


class MARGINS(Structure):
    _fields_ = [
        ("cxLeftWidth",     c_int),
        ("cxRightWidth",    c_int),
        ("cyTopHeight",     c_int),
        ("cyBottomHeight",  c_int),
    ]

class WindowsEffectHelper:
    """Applies the DWM frame effects to a frameless Qt window."""

    def __init__(self):
        # C Libraries which are really necessary to apply Windows OS effect to Qt frameless window
        dwmapi = windll.LoadLibrary("dwmapi")

        self.__dwmExtendFrameIntoClientArea = dwmapi.DwmExtendFrameIntoClientArea
        self.__dwmSetWindowAttribute = dwmapi.DwmSetWindowAttribute

    def setBasicEffect(self, hWnd, hint):
        """Extend the DWM frame into the client area, round the corners and set the window style from the hint buttons."""
        hWnd = int(hWnd)
        margins = MARGINS(-1, -1, -1, -1)
        self.__dwmExtendFrameIntoClientArea(hWnd, byref(margins))

        # Disabilita i pulsanti DWM nativi
        DWMWA_CAPTION_BUTTON_BOUNDS = 5
        disable = c_int(0)
        self.__dwmSetWindowAttribute(hWnd, DWMWA_CAPTION_BUTTON_BOUNDS, byref(disable), 4)

        # Windows 11 rounds the frame. Windows 10 rejects this attribute and keeps square corners.
        DWMWA_WINDOW_CORNER_PREFERENCE = 33
        DWMWCP_ROUND = c_int(2)
        self.__dwmSetWindowAttribute(hWnd, DWMWA_WINDOW_CORNER_PREFERENCE, byref(DWMWCP_ROUND), 4)

        # WS_THICKFRAME lets Windows resize every window, including the auxiliary windows.
        dwNewLong = win32con.WS_CAPTION | win32con.WS_THICKFRAME
        if 'close' in hint and len(hint) == 1:
            pass
        else:
            if 'min' in hint:
                dwNewLong |= win32con.WS_MINIMIZEBOX
            if 'max' in hint:
                dwNewLong |= win32con.CS_DBLCLKS | win32con.WS_MAXIMIZEBOX

        dwNewLong &= ~win32con.WS_SYSMENU
        win32gui.SetWindowLong(hWnd, win32con.GWL_STYLE, dwNewLong)