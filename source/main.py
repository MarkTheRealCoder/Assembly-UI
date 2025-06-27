import faulthandler
import os
import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from source.filesystem import find_path
from source.interface import MainWindow
from source.interface.assets import add_fonts, translateQSS
from source.platform import Desktop

if __name__ == "__main__":
    # Verifica se l'applicazione è in modalità frozen (eseguibile)
    if getattr(sys, 'frozen', False):
        # Se l'applicazione è congelata (exe), reindirizza stderr a un file
        log_path = os.path.join(os.path.dirname(sys.executable), 'error.log')
        sys.stderr = open(log_path, 'w')
    
    faulthandler.enable()
    QApplication.setApplicationName("Assembly Stdio")
    QApplication.setApplicationDisplayName("Assembly Stdio")
    QApplication.setApplicationVersion("1.0")
    QApplication.setOrganizationName("Assembly Stdio")
    QApplication.setOrganizationDomain("Assembly Stdio")
    QApplication.setQuitOnLastWindowClosed(True)
    app = QApplication(sys.argv)
    with open(find_path("style.qss"), "r") as f:
        app.setStyleSheet(translateQSS(f.read()))
    Desktop.setDesktopSize(QDesktopWidget().screenGeometry().size())
    add_fonts()
    window: MainWindow = MainWindow()
    window.show()
    sys.exit(app.exec_())


# todo: Modify Window layout to add minimal borders for resizing
# todo: Create options window
# todo: Create buttons for Debug interface
# todo: Refactor code for Debugger Memory view
# todo: Create a JPype impl for using Antonio's Java code
# todo: Refactor avoiding circular imports (LAST)
