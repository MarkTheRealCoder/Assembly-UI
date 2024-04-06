import os
import sys

from PyQt5.QtWidgets import QApplication, QDesktopWidget

from graphics.Graphics import Window as MainWindow
from src.tools.Tools import Desktop

if __name__ == "__main__":
    app = QApplication(sys.argv)
    Desktop.setDesktopSize(QDesktopWidget().screenGeometry().size())
    window: MainWindow = MainWindow(app)
    window.show()
    sys.exit(app.exec_())


# print("0x" + "{0:08x}".format(1000).upper())

# todo Fixare/Implementare il sistema di ingrandimento della finestra                                           MIDDLE
# todo Impostare i pulsanti per lo scorrimento del risultato della risposta dal server                          MIDDLE
# todo Collegare Input e Output                                                                                 LAST
# todo Predisporre il sistema di richieste al server                                                            LAST
# todo Aggiungere e sistemare le sezioni dei vari menù                                                          MIDDLE
# todo Impedire che con la rotella del mouse si possa cambiare TAB                                              FIRST
# todo rimuovere i pulsanti per scorrere le TAB quando non c'è abbastanza spazio                                FIRST
# todo fixare i doppi accapo che rimangono salvati nei file ad ogni prelievo del testo dall'editor              FIRST


