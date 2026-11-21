import ctypes
import logging
from functools import lru_cache
from pathlib import Path

from PyQt5 import sip
from PyQt5.QtGui import QGuiApplication


TILED_RESIZE_EDGES_PROPERTY = "gnomeTiledResizeEdges"


@lru_cache(maxsize=1)
def _load_monitor():
    project = Path(__file__).resolve().parents[4]
    library_path = project / "build" / "gnome-tiling" / "libassembly-gnome-tiling.so"
    if not library_path.is_file():
        return None
    try:
        library = ctypes.CDLL(str(library_path))
        monitor = library.assembly_watch_gnome_tiling_v2
    except (OSError, AttributeError) as error:
        logging.getLogger(__name__).warning("Could not load GNOME tiling support: %s", error)
        return None
    monitor.argtypes = (ctypes.c_void_p,)
    monitor.restype = None
    return monitor


def watch_gnome_tiling(window):
    if QGuiApplication.platformName().startswith("wayland"):
        monitor = _load_monitor()
        if monitor is not None:
            monitor(sip.unwrapinstance(window))
