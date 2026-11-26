from __future__ import annotations

import os
import shutil
import sys
from functools import lru_cache
from pathlib import Path

import psutil
from PyQt5.QtCore import QCoreApplication, QStandardPaths, QUrl
from PyQt5.QtGui import QDesktopServices

from source.platform import isWindows

if isWindows():
    import win32api
    import win32con


def app_root() -> str:
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return str(Path(__file__).resolve().parents[2])


def resources_root() -> str:
    root = app_root()
    resources = os.path.join(root, "resources")
    return resources if os.path.isdir(resources) else root


def settings_path() -> str:
    if not getattr(sys, "frozen", False):
        return os.path.join(app_root(), "settings.ini")

    # A packaged app can live in a read-only location.
    QCoreApplication.setOrganizationName("Assembly Stdio")
    QCoreApplication.setApplicationName("Assembly Stdio")
    location = QStandardPaths.writableLocation(QStandardPaths.AppConfigLocation)
    os.makedirs(location, exist_ok=True)
    path = os.path.join(location, "settings.ini")
    legacy = os.path.join(os.path.dirname(sys.executable), "settings.ini")
    if not os.path.exists(path) and os.path.isfile(legacy):
        shutil.copy2(legacy, path)
    return path


@lru_cache(maxsize=None)
def find_path(file: str) -> str:
    location = resources_root()
    result: str = ""
    for root, _dir, files in os.walk(location):
        if file in files:
            result = os.path.join(root, file)
            break
    return result


def get_available_disks():
    partitions = psutil.disk_partitions(all=False)
    if isWindows():
        return [partition.device[:-1] for partition in partitions if "cdrom" not in partition.opts]
    return list(dict.fromkeys(
        partition.mountpoint for partition in partitions if partition.mountpoint
    ))


def resolve_app_path(ui_path: str) -> str:
    from source.filesystem.documents import Document
    from source.interface import Settings

    root = os.path.normpath(Settings.get("application/cwd"))
    path = ui_path or ""

    if path.startswith(root + os.sep) or path == root:
        return os.path.normpath(path)

    relative = path.removeprefix(Document.SEP).strip("/\\")
    if not relative:
        return root
    return os.path.normpath(os.path.join(root, relative))


def to_ui_path(absolute_path: str) -> str:
    from source.filesystem.documents import Document
    from source.interface import Settings

    root = os.path.normpath(Settings.get("application/cwd"))
    abs_norm = os.path.normpath(absolute_path.rstrip("/\\"))
    if abs_norm == root:
        return Document.SEP
    if abs_norm.startswith(root + os.sep):
        rel = abs_norm[len(root):].lstrip("/\\").replace(os.sep, Document.SEP)
        return Document.SEP + rel
    return Document.SEP + abs_norm.replace(os.sep, Document.SEP)


def find_dir(directory: str) -> str:
    location = resources_root()
    result: str = ""
    for root, directories, files in os.walk(location):
        if directory in directories:
            result = os.path.join(root, directory)
            break
    return result


def open_dir(path: str):
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))


def is_file_hidden(file: str, path: str) -> bool:
    if isWindows():
        try:
            attribute = win32api.GetFileAttributes(path)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM) != 0
        except Exception as e:
            del e
            return False
    return file.startswith(".")


def ls(path: str, exts: tuple = ()):
    results: list[tuple[str, str]] = []
    extensions = {ext.lower() for ext in exts}
    try:
        with os.scandir(path) as entries:
            for entry in entries:
                if is_file_hidden(entry.name, entry.path):
                    continue
                if entry.is_dir():
                    results.append((entry.name, ""))
                else:
                    extension = os.path.splitext(entry.name)[1][1:].lower()
                    if extension in extensions and entry.is_file():
                        results.append((entry.name, extension))
    except OSError:
        pass
    return results


def create_dir(path: str, name: str) -> bool:
    if not name.strip():
        return False
    try:
        os.mkdir(os.path.join(path, name))
    except (FileExistsError, FileNotFoundError, OSError):
        return False
    return True


def create_file(path: str, name: str, ext: str) -> Path | None:
    directory = os.path.normpath(path)
    if not os.path.isdir(directory):
        return None
    file = Path(directory) / f"{name}.{ext}"
    if file.exists():
        return None
    try:
        file.touch()
        return file
    except OSError:
        return None
