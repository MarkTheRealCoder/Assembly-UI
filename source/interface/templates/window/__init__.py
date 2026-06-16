from source.platform import isWindows

if isWindows():
    from .base_win import BaseWindow, native_maximize, native_restore, native_minimize
else:
    from .base_unix import BaseWindow, native_maximize, native_restore, native_minimize

__all__ = ["BaseWindow", "native_maximize", "native_restore", "native_minimize"]
