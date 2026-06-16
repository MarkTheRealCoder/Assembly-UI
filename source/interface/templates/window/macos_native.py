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


class TilingMenuTarget(Cocoa.NSObject):
    def initWithWindow_(self, ns_window):
        self = objc.super(TilingMenuTarget, self).init()
        if self is None:
            return None
        self._ns_window = ns_window
        return self

    def tileLeft_(self, _sender):
        self._ns_window._tileLeft_(None)

    def tileRight_(self, _sender):
        self._ns_window._tileRight_(None)

    def zoomTop_(self, _sender):
        self._ns_window._zoomTop_(None)

    def zoomBottom_(self, _sender):
        self._ns_window._zoomBottom_(None)

    def zoomTopLeft_(self, _sender):
        self._ns_window._zoomTopLeft_(None)

    def zoomTopRight_(self, _sender):
        self._ns_window._zoomTopRight_(None)

    def zoomBottomLeft_(self, _sender):
        self._ns_window._zoomBottomLeft_(None)

    def zoomBottomRight_(self, _sender):
        self._ns_window._zoomBottomRight_(None)

    def zoomFill_(self, _sender):
        self._ns_window._zoomFill_(None)

    def zoomCenter_(self, _sender):
        self._ns_window._zoomCenter_(None)


def _clone_menu_item(item):
    if item is None:
        return None
    cloned = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        item.title(), item.action(), item.keyEquivalent()
    )
    cloned.setTarget_(item.target())
    cloned.setEnabled_(item.isEnabled())
    submenu = item.submenu()
    if submenu is not None:
        cloned.setSubmenu_(_clone_menu(submenu))
    return cloned


def _clone_menu(menu):
    cloned_menu = Cocoa.NSMenu.alloc().initWithTitle_(menu.title())
    for index in range(menu.numberOfItems()):
        item = menu.itemAtIndex_(index)
        if item is None:
            continue
        if item.isSeparatorItem():
            cloned_menu.addItem_(Cocoa.NSMenuItem.separatorItem())
            continue
        cloned_menu.addItem_(_clone_menu_item(item))
    return cloned_menu


def _add_menu_item(menu, title, target, action):
    item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(title, action, "")
    item.setTarget_(target)
    menu.addItem_(item)


def build_tiling_menu(ns_window):
    menu = Cocoa.NSMenu.alloc().initWithTitle_("Window")
    target = TilingMenuTarget.alloc().initWithWindow_(ns_window)

    move_menu = Cocoa.NSMenu.alloc().initWithTitle_("Move & Resize")
    _add_menu_item(move_menu, "Left of Screen", target, "tileLeft:")
    _add_menu_item(move_menu, "Right of Screen", target, "tileRight:")
    _add_menu_item(move_menu, "Top", target, "zoomTop:")
    _add_menu_item(move_menu, "Bottom", target, "zoomBottom:")
    move_menu.addItem_(Cocoa.NSMenuItem.separatorItem())
    _add_menu_item(move_menu, "Top Left", target, "zoomTopLeft:")
    _add_menu_item(move_menu, "Top Right", target, "zoomTopRight:")
    _add_menu_item(move_menu, "Bottom Left", target, "zoomBottomLeft:")
    _add_menu_item(move_menu, "Bottom Right", target, "zoomBottomRight:")

    move_item = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
        "Move & Resize", None, ""
    )
    move_item.setSubmenu_(move_menu)
    menu.addItem_(move_item)

    _add_menu_item(menu, "Fill", target, "zoomFill:")
    _add_menu_item(menu, "Center", target, "zoomCenter:")

    system_menu = ns_window._windowTilingMenu()
    if system_menu is not None:
        for index in range(system_menu.numberOfItems()):
            system_item = system_menu.itemAtIndex_(index)
            if system_item is None:
                continue
            submenu = system_item.submenu()
            if submenu is not None:
                cloned = Cocoa.NSMenuItem.alloc().initWithTitle_action_keyEquivalent_(
                    system_item.title(), None, ""
                )
                cloned.setSubmenu_(_clone_menu(submenu))
            else:
                cloned = _clone_menu_item(system_item)
            menu.addItem_(cloned)

    return menu, target


def show_tiling_menu_at_widget(window_widget, qt_button):
    ns_window = _ns_window(window_widget)
    menu, target = build_tiling_menu(ns_window)

    anchor = qt_button.mapToGlobal(qt_button.rect().bottomLeft())
    screen = qt_button.screen()
    if screen is not None:
        screen_height = screen.geometry().height()
    else:
        screen_height = Cocoa.NSScreen.mainScreen().frame().size.height
    ns_point = Cocoa.NSPoint(anchor.x(), screen_height - anchor.y())
    menu.popUpMenuPositioningItem_atLocation_inView_(None, ns_point, None)
    return target
