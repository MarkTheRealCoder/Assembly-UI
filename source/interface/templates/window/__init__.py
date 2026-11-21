from source.platform import isMac, isWindows

if isWindows():
    from .base_win import BaseWindow, native_maximize, native_restore, native_minimize
elif isMac():
    from .base_macos import BaseWindow, native_maximize, native_restore, native_minimize
else:
    from .base_linux import BaseWindow, native_maximize, native_restore, native_minimize

__all__ = ["BaseWindow", "native_maximize", "native_restore", "native_minimize"]
