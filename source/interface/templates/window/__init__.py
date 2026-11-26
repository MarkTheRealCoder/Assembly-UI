from source.platform import isMac, isWindows

if isWindows():
    from .base_win import BaseWindow, native_maximize, native_restore, native_minimize
elif isMac():
    from .base_macos import BaseWindow, native_maximize, native_restore, native_minimize
    from .base_linux import ResizeFrame
else:
    from .base_linux import BaseWindow, native_maximize, native_restore, native_minimize, ResizeFrame

__all__ = ["BaseWindow", "native_maximize", "native_restore", "native_minimize"]
# The ResizeFrame wraps the frameless windows on Linux and macOS only.
if not isWindows():
    __all__.append("ResizeFrame")
