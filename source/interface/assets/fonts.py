from PyQt5.QtGui import QFontDatabase

from source.filesystem import find_path


def add_fonts():
    QFontDatabase.addApplicationFont(find_path("AnonymousPro.ttf"))
    QFontDatabase.addApplicationFont(find_path("FiraCode.ttf"))
    QFontDatabase.addApplicationFont(find_path("Inconsolata.ttf"))
    QFontDatabase.addApplicationFont(find_path("Bahnschrift.ttf"))
    QFontDatabase.addApplicationFont(find_path("Monaco.ttf"))
    QFontDatabase.addApplicationFont(find_path("Fixedsys.ttf"))
    QFontDatabase.addApplicationFont(find_path("OCR-A.ttf"))