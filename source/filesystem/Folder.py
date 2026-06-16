from __future__ import annotations

import os
import re
from pathlib import Path

import psutil
from PyQt5.QtCore import QUrl
from PyQt5.QtGui import QDesktopServices

from source.platform import isWindows

if isWindows():
    import win32api
    import win32con


def find_path(file: str) -> str:
    location = os.getcwd()
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
    from source.interface.shared import Settings

    root = os.path.normpath(Settings.application_cwd())
    path = ui_path or ""

    if path.startswith(root + os.sep) or path == root:
        return os.path.normpath(path)

    relative = path.removeprefix(Document.SEP).strip("/\\")
    if not relative:
        return root
    return os.path.normpath(os.path.join(root, relative))


def to_ui_path(absolute_path: str) -> str:
    from source.filesystem.documents import Document
    from source.interface.shared import Settings

    root = os.path.normpath(Settings.application_cwd())
    abs_norm = os.path.normpath(absolute_path.rstrip("/\\"))
    if abs_norm == root:
        return Document.SEP
    if abs_norm.startswith(root + os.sep):
        rel = abs_norm[len(root):].lstrip("/\\").replace(os.sep, Document.SEP)
        return Document.SEP + rel
    return Document.SEP + abs_norm.replace(os.sep, Document.SEP)


def find_dir(directory: str) -> str:
    location = os.getcwd()
    result: str = ""
    for root, directories, files in os.walk(location):
        if directory in directories:
            result = os.path.join(root, directory)
            break
    return result


def open_dir(path: str):
    print("DIDIT")
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))
    print("DIDIT")


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
    try:
        dirs = os.listdir(path)
        for i in dirs:
            file = None
            valid = False
            if exts != ():
                file = re.match(fr"\b\w+\.({'|'.join(exts)})\b", i)
                valid = file is not None
            if not valid:
                fp = os.path.join(path, i)  # full path
                valid = os.path.isdir(fp) and not is_file_hidden(i, fp)
            if valid:
                ext = "" if file is None else file.group(1)
                results.append((i, ext))
    except Exception:
        pass
    finally:
        pass
    return results


def create_dir(path: str, name: str) -> bool:
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
