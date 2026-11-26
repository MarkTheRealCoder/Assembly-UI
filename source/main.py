import faulthandler
import os
import sys
import tempfile
from pathlib import Path

_ROOT = Path(__file__).resolve().parent.parent
if str(_ROOT) not in sys.path:
    sys.path.insert(0, str(_ROOT))

from PyQt5.QtCore import QStandardPaths, QTimer
from PyQt5.QtWidgets import QApplication, QDesktopWidget

from source.comms.events import ClosingEvent
from source.comms.handlers import EventRegister
from source.filesystem import find_path
from source.interface import MainWindow, Settings
from source.interface.assets import add_fonts, translateQSS
from source.interface.modals import warmUpWebEngine
from source.platform import Desktop, isLinux


def _redirect_stderr() -> None:
    """Send stderr to error.log in the user data folder, or the temp folder if that fails."""
    candidates = (
        lambda: QStandardPaths.writableLocation(QStandardPaths.AppDataLocation),
        tempfile.gettempdir,
    )
    for location in candidates:
        try:
            folder = location()
            if not folder:
                continue
            os.makedirs(folder, exist_ok=True)
            sys.stderr = open(os.path.join(folder, 'error.log'), 'w')
            return
        except OSError:
            continue


if __name__ == "__main__":
    # The names decide the user data folder, so set them before the redirect.
    QApplication.setApplicationName("Assembly Stdio")
    QApplication.setApplicationDisplayName("Assembly Stdio")
    QApplication.setApplicationVersion("1.0")
    QApplication.setOrganizationName("Assembly Stdio")
    QApplication.setOrganizationDomain("assemblystdio.dev")

    if getattr(sys, 'frozen', False):
        # A frozen executable has no console, so stderr goes to a file.
        _redirect_stderr()

    faulthandler.enable()
    QApplication.setQuitOnLastWindowClosed(True)

    # Use native Wayland to receive GNOME's window tiling events.
    if isLinux() and os.environ.get("XDG_SESSION_TYPE") == "wayland":
        desktops = os.environ.get("XDG_CURRENT_DESKTOP", "").lower().split(":")
        if "gnome" in desktops:
            os.environ.setdefault("QT_QPA_PLATFORM", "wayland;xcb")

    app = QApplication(sys.argv)
    app.aboutToQuit.connect(lambda: EventRegister.send(ClosingEvent(), "Main"))
    with open(find_path("style.qss"), "r") as f:
        app.setStyleSheet(translateQSS(f.read()))
    Desktop.setDesktopSize(QDesktopWidget().screenGeometry().size())
    add_fonts()
    Settings.base_dir()
    window: MainWindow = MainWindow()
    window.show()
    window.raise_()
    if not app.platformName().startswith("wayland"):
        window.activateWindow()
    window.setFocus()
    # Start the web engine while no program runs, so the first help page does not block a run.
    QTimer.singleShot(0, warmUpWebEngine)
    sys.exit(app.exec_())

# todo: Modify titlebar and main window to match OS signals

# todo: Implement differentiation for OSs: Layout maker for the Titlebar
#  and Unix-like Window handling for MacOS and Linux
