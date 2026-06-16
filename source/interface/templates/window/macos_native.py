"""Keep native NSWindow frame on macOS so Split View / edge tiling works."""
from ctypes import c_void_p

import Cocoa
import objc


def _ns_window(widget):
    view = objc.objc_object(c_void_p=int(widget.winId()))
    return view.window()


def configure_hidden_titlebar(widget):
    ns_window = _ns_window(widget)
    ns_window.setStyleMask_(
        ns_window.styleMask() | Cocoa.NSFullSizeContentViewWindowMask
    )
    ns_window.setTitlebarAppearsTransparent_(True)
    ns_window.setMovableByWindowBackground_(False)
    ns_window.setMovable_(False)
    ns_window.setTitleVisibility_(Cocoa.NSWindowTitleHidden)
    for button_type in (
        Cocoa.NSWindowCloseButton,
        Cocoa.NSWindowMiniaturizeButton,
        Cocoa.NSWindowZoomButton,
    ):
        button = ns_window.standardWindowButton_(button_type)
        if button is not None:
            button.setHidden_(True)
