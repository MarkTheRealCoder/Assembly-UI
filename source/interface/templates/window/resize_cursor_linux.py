import ctypes
import math
import os
import subprocess

from PyQt5.QtGui import QCursor, QGuiApplication, QImage, QPixmap


class _XcursorImage(ctypes.Structure):
    _fields_ = [
        ("version", ctypes.c_uint32),
        ("size", ctypes.c_uint32),
        ("width", ctypes.c_uint32),
        ("height", ctypes.c_uint32),
        ("xhot", ctypes.c_uint32),
        ("yhot", ctypes.c_uint32),
        ("delay", ctypes.c_uint32),
        ("pixels", ctypes.POINTER(ctypes.c_uint32)),
    ]


def _gnome_setting(key):
    try:
        value = subprocess.check_output(
            ["gsettings", "get", "org.gnome.desktop.interface", key],
            stderr=subprocess.DEVNULL, text=True, timeout=0.4,
        )
        return value.strip().strip("'")
    except (OSError, subprocess.SubprocessError):
        return ""


class LinuxResizeCursors:
    def __init__(self):
        self._cache = {}
        self._library = None
        try:
            library = ctypes.CDLL("libXcursor.so.1")
            image_pointer = ctypes.POINTER(_XcursorImage)
            library.XcursorLibraryLoadImage.argtypes = (ctypes.c_char_p, ctypes.c_char_p, ctypes.c_int)
            library.XcursorLibraryLoadImage.restype = image_pointer
            library.XcursorImageDestroy.argtypes = (image_pointer,)
            library.XcursorImageDestroy.restype = None
        except (OSError, AttributeError):
            return

        self._library = library
        theme = os.environ.get("XCURSOR_THEME", "")
        size = os.environ.get("XCURSOR_SIZE", "")
        if "gnome" in os.environ.get("XDG_CURRENT_DESKTOP", "").lower().split(":"):
            theme = _gnome_setting("cursor-theme") or theme
            size = _gnome_setting("cursor-size") or size
        self._theme = os.fsencode(theme) if theme else None
        try:
            self._size = int(size)
        except ValueError:
            self._size = 0
        if self._size <= 0:
            self._size = 24
        self._wayland = QGuiApplication.platformName().startswith("wayland")

    def cursor(self, name, fallback, device_pixel_ratio=1.0):
        scale = max(1, math.ceil(device_pixel_ratio))
        key = (name, scale)
        if key not in self._cache:
            themed_cursor = self._load_cursor(name, scale)
            self._cache[key] = themed_cursor if themed_cursor is not None else QCursor(fallback)
        return self._cache[key]

    def _load_cursor(self, name, scale):
        if self._library is None:
            return None
        # Load the image from the theme without an X11 display connection.
        image_pointer = self._library.XcursorLibraryLoadImage(name.encode("ascii"), self._theme, self._size * scale)
        if not image_pointer:
            return None

        try:
            image = image_pointer.contents
            stride = image.width * ctypes.sizeof(ctypes.c_uint32)
            pixels = ctypes.string_at(image.pixels, stride * image.height)
            bitmap = QImage(pixels, image.width, image.height, stride, QImage.Format_ARGB32_Premultiplied)
            pixmap = QPixmap.fromImage(bitmap.copy())
            if pixmap.isNull():
                return None
            pixmap.setDevicePixelRatio(scale)
            # Wayland uses surface coordinates for the hotspot, while X11 uses pixels.
            hotspot_scale = scale if self._wayland else 1
            return QCursor(pixmap, round(image.xhot / hotspot_scale), round(image.yhot / hotspot_scale))
        finally:
            self._library.XcursorImageDestroy(image_pointer)
