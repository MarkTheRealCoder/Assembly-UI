import ctypes
import logging
from functools import lru_cache
from pathlib import Path

from PyQt5 import sip
from PyQt5.QtCore import qVersion
from PyQt5.QtGui import QGuiApplication


TILED_RESIZE_EDGES_PROPERTY = "gnomeTiledResizeEdges"


@lru_cache(maxsize=1)
def _load_monitor():
    """Load the GNOME tiling module once and return its watch function, or None if it is missing or built for another Qt version."""
    project = Path(__file__).resolve().parents[4]
    library_path = project / "build" / "gnome-tiling" / "libassembly-gnome-tiling.so"
    if not library_path.is_file():
        return None
    try:
        library = ctypes.CDLL(str(library_path))
        monitor = library.assembly_watch_gnome_tiling_v2
        built_version = library.assembly_gnome_tiling_qt_version
    except (OSError, AttributeError) as error:
        logging.getLogger(__name__).warning("Could not load GNOME tiling support: %s", error)
        return None
    # The module uses Qt private headers, which are valid only for the exact Qt version.
    built_version.argtypes = ()
    built_version.restype = ctypes.c_char_p
    built = built_version().decode("ascii")
    if built != qVersion():
        logging.getLogger(__name__).warning(
            "GNOME tiling support is off: the module uses Qt %s, but the app runs on Qt %s.",
            built, qVersion(),
        )
        return None
    monitor.argtypes = (ctypes.c_void_p,)
    monitor.restype = None
    return monitor


def watch_gnome_tiling(window):
    """Watch the GNOME tiling state of the window on Wayland and publish it as a property of the window."""
    if QGuiApplication.platformName().startswith("wayland"):
        monitor = _load_monitor()
        if monitor is not None:
            monitor(sip.unwrapinstance(window))
