import sys

from PyQt5.QtWidgets import QApplication

from Graphics.graphics import Window as MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window: MainWindow = MainWindow(app)
    window.show()
    sys.exit(app.exec_())

