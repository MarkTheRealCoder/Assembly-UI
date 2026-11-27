"""
Renders resources/icons/Logo.svg to the icon of the executable: .ico for Windows, .icns for macOS.

    python packaging/make_icon.py <output .ico or .icns>
"""
import io
import os
import sys

from PIL import Image
from PyQt5.QtCore import QBuffer, QByteArray, QIODevice, Qt
from PyQt5.QtGui import QGuiApplication, QImage, QPainter
from PyQt5.QtSvg import QSvgRenderer

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
ICO_SIZES = [16, 24, 32, 48, 64, 128, 256]
# The .icns writer of Pillow makes the smaller sizes from a 1024 px image.
RENDER_SIZE = 1024


def main() -> int:
    os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
    app = QGuiApplication(sys.argv[:1])
    renderer = QSvgRenderer(os.path.join(ROOT, "resources", "icons", "Logo.svg"))
    if not renderer.isValid():
        print("Logo.svg is not a valid SVG")
        return 1
    image = QImage(RENDER_SIZE, RENDER_SIZE, QImage.Format_ARGB32)
    image.fill(Qt.transparent)
    painter = QPainter(image)
    renderer.render(painter)
    painter.end()

    data = QByteArray()
    buffer = QBuffer(data)
    buffer.open(QIODevice.WriteOnly)
    image.save(buffer, "PNG")
    icon = Image.open(io.BytesIO(bytes(data)))
    if sys.argv[1].lower().endswith(".icns"):
        icon.save(sys.argv[1], format="ICNS")
    else:
        icon.save(sys.argv[1], format="ICO", sizes=[(size, size) for size in ICO_SIZES])
    del app
    print(f"Icon written to {sys.argv[1]}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
