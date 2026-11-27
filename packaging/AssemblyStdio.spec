# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec for the folder build of Assembly Stdio, on Windows, Linux and macOS.

Run from the project folder:
    pyinstaller --noconfirm --clean packaging/AssemblyStdio.spec

The result is dist/AssemblyStdio/ on Windows and Linux, and dist/AssemblyStdio.app on macOS.
packaging/assemble.py then adds runtime/ (the Java runtime made with jlink) and licenses/.
"""
import os
import sys

from PyInstaller.utils.hooks import collect_data_files

ROOT = os.path.abspath(os.path.join(SPECPATH, os.pardir))
VERSION = os.environ.get("APP_VERSION", "1.0.0")
MACOS = sys.platform == "darwin"
# packaging/make_icon.py writes the icon of the platform: .ico for Windows, .icns for macOS.
ICON = os.path.join(ROOT, "build", "AssemblyStdio.icns" if MACOS else "AssemblyStdio.ico")

# find_path() looks for the files under _MEIPASS/resources, so the folder keeps its name.
# It also contains interpreter.jar, in resources/antlr_lexers/.
datas = [(os.path.join(ROOT, "resources"), "resources")]
# pyqttoast loads its stylesheets and icons from its package folder.
datas += collect_data_files("pyqttoast")

a = Analysis(
    [os.path.join(ROOT, "source", "main.py")],
    pathex=[ROOT],
    binaries=[],
    datas=datas,
    hiddenimports=[],
    hookspath=[],
    runtime_hooks=[],
    excludes=["tkinter"],
    noarchive=False,
)

# QtWebEngine needs QtQml and QtQuick, and their PyInstaller hooks also collect every QML plugin and the
# Qt libraries they use (Quick 3D, Multimedia, Location, Bluetooth...). The app uses no QML, so they are dropped.
# On macOS the Qt libraries are frameworks, whose names do not match these prefixes: only the QML folder goes.
UNUSED_QT = (
    "Qt5Bluetooth", "Qt5Location", "Qt5Multimedia", "Qt5Nfc", "Qt5Quick3D", "Qt5QuickControls2",
    "Qt5QuickParticles", "Qt5QuickShapes", "Qt5QuickTemplates2", "Qt5QuickTest", "Qt5RemoteObjects",
    "Qt5Sensors", "Qt5SerialPort", "Qt5Test", "Qt5TextToSpeech", "Qt5XmlPatterns", "Qt5Sql",
)


def _used(entry) -> bool:
    destination = entry[0].replace("\\", "/")
    name = os.path.basename(destination)
    if "/Qt5/qml/" in destination or "/Qt/qml/" in destination:
        return False
    return not any(name.startswith(prefix) or name.startswith("lib" + prefix) for prefix in UNUSED_QT)


a.binaries = [entry for entry in a.binaries if _used(entry)]
a.datas = [entry for entry in a.datas if _used(entry)]

pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name="AssemblyStdio",
    console=False,
    upx=False,
    icon=ICON if os.path.isfile(ICON) else None,
)

coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    upx=False,
    name="AssemblyStdio",
)

if MACOS:
    app = BUNDLE(
        coll,
        name="AssemblyStdio.app",
        icon=ICON if os.path.isfile(ICON) else None,
        bundle_identifier="dev.assemblystdio.AssemblyStdio",
        version=VERSION,
        info_plist={
            "CFBundleDisplayName": "Assembly Stdio",
            "CFBundleName": "Assembly Stdio",
            "NSHighResolutionCapable": True,
        },
    )
