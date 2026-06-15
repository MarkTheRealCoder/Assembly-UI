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

    def __init__(self):
        # C Libraries which are really necessary to apply Windows OS effect to Qt frameless window
        user32 = windll.LoadLibrary("user32")
        dwmapi = windll.LoadLibrary("dwmapi")

        self.__windowCompositionAttribute = user32.SetWindowCompositionAttribute
        self.__dwmExtendFrameIntoClientArea = dwmapi.DwmExtendFrameIntoClientArea
        self.__dwmSetWindowAttribute = dwmapi.DwmSetWindowAttribute

    # set fancy effect
    def setBasicEffect(self, hWnd, hint):
        hWnd = int(hWnd)
        margins = MARGINS(-1, -1, -1, -1)
        self.__dwmExtendFrameIntoClientArea(hWnd, byref(margins))

        # Disabilita i pulsanti DWM nativi
        DWMWA_CAPTION_BUTTON_BOUNDS = 5
        DWMWA_NONCLIENT_RTL_LAYOUT = 6
        disable = c_int(0)
        self.__dwmSetWindowAttribute(hWnd, DWMWA_CAPTION_BUTTON_BOUNDS, byref(disable), 4)

        dwNewLong = win32con.WS_CAPTION
        if 'close' in hint and len(hint) == 1:
            pass
        else:
            if 'min' in hint:
                dwNewLong |= win32con.WS_MINIMIZEBOX
            if 'max' in hint:
                dwNewLong |= win32con.CS_DBLCLKS | win32con.WS_THICKFRAME | win32con.WS_MAXIMIZEBOX

        dwNewLong &= ~win32con.WS_SYSMENU
        win32gui.SetWindowLong(hWnd, win32con.GWL_STYLE, dwNewLong)