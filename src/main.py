import faulthandler
# import os
import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from src.interface.Graphics import Window as MainWindow
from src.platform.Adaptability import Desktop

if __name__ == "__main__":
    faulthandler.enable()
    app = QApplication(sys.argv)
    Desktop.setDesktopSize(QDesktopWidget().screenGeometry().size())
    window: MainWindow = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


# print("0x" + "{0:08x}".format(1000).upper())

# todo Impostare i pulsanti per lo scorrimento del risultato della risposta dal server                          MIDDLE
# todo Collegare Input e Output                                                                                 LAST
# todo Predisporre il sistema di richieste al server                                                            LAST
# todo Aggiungere e sistemare le sezioni dei vari menù                                                          MIDDLE

# todo Eliminare tutti i CloseButton e sostituirli con specifiche estensioni di CloseButton

