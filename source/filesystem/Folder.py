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
    disks = [partition.device[:-1] for partition in partitions if "cdrom" not in partition.opts]
    return disks


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
        os.mkdir(path + name)
    except FileExistsError or FileNotFoundError:
        return False
    return True


def create_file(path: str, name: str, ext: str) -> bool:
    file = Path(path + f"{name}.{ext}")
    if not file.exists():
        try:
            file.touch()
            return True
        except FileExistsError:
            return False
    return False
