from typing import Optional

from PyQt5.QtGui import QFont, QFontDatabase

from source.filesystem import find_path

# Font of the code editors: the first family installed or bundled is used.
EDITOR_FAMILIES = ("JetBrains Mono", "Cascadia Mono", "Consolas", "Monospace")
EDITOR_FONT_SIZE = 11

_JETBRAINS_MONO = (
    "JetBrainsMono-Regular.ttf", "JetBrainsMono-Italic.ttf", "JetBrainsMono-SemiBold.ttf", "JetBrainsMono-Bold.ttf"
)
_editor_family: Optional[str] = None


def add_fonts():
    """ Register the bundled fonts with the application """
    QFontDatabase.addApplicationFont(find_path("AnonymousPro.ttf"))
    QFontDatabase.addApplicationFont(find_path("FiraCode.ttf"))
    QFontDatabase.addApplicationFont(find_path("Fixedsys.ttf"))
    for file in _JETBRAINS_MONO:
        QFontDatabase.addApplicationFont(find_path(file))


def editorFamily() -> str:
    """ Return the first available family of EDITOR_FAMILIES, falling back to the system monospace font """
    global _editor_family
    if _editor_family is None:
        available = set(QFontDatabase().families())
        _editor_family = next((family for family in EDITOR_FAMILIES if family in available), None)
        if _editor_family is None:
            _editor_family = QFontDatabase.systemFont(QFontDatabase.FixedFont).family()
    return _editor_family


def editorFont(size: int = EDITOR_FONT_SIZE, weight: int = QFont.Normal, italic: bool = False) -> QFont:
    """ Monospaced font of the code editors """
    family = editorFamily()
    # On Windows the semibold face of a bundled font is registered as its own family, such as
    # "JetBrains Mono SemiBold": asking the main family for that weight would give a synthetic bold.
    if weight == QFont.DemiBold and f"{family} SemiBold" in QFontDatabase().families():
        family, weight = f"{family} SemiBold", QFont.Normal
    font = QFont(family, size, weight, italic)
    font.setStyleHint(QFont.Monospace)
    font.setFixedPitch(True)
    return font
