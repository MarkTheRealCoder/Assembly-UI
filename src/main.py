
import sys

from PyQt5.QtWidgets import QApplication

from graphics.Graphics import Window as MainWindow

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window: MainWindow = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


# print("0x" + "{0:08x}".format(1000).upper())

