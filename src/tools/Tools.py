import json
import os
import re
from typing import Any, Literal, Iterable

import psutil
from PyQt5.QtCore import QUrl, QSize
from PyQt5.QtGui import QDesktopServices
from PyQt5.QtWidgets import QWidget, QLayout, QDesktopWidget
from regex import regex

if os.name == "nt":
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
    finally:
        pass
    return results


def translateQSS(style: str):
    variables: dict[str: str] = {}
    index = style.find("variables")
    last_index = style.find("}", index)
    substring_variables = style[index:last_index]
    substring_variables = substring_variables.replace("variables", "").replace("{", "")
    raw = substring_variables.split(";")  # comments_free.split(";")
    for i in raw:
        try:
            k, v = i.split(":")
            variables[k.strip()] = v.strip()
        except Exception as e:
            del e
    style = style[last_index + 1:]
    matches: list[regex.Match] = regex.findall(r"(var\s*\((.*)\))", style)
    for s, r in matches:
        style = style.replace(s, variables.get(r))
    return style


def isWindows():
    return os.name == "nt"


def createLayout(l: type, parent: QWidget):
    layout = l(parent)
    layout.setContentsMargins(0, 0, 0, 0)
    layout.setSpacing(0)
    layout.setSizeConstraint(QLayout.SetNoConstraint)
    return layout


class Desktop:
    DESKTOP_SIZE: QSize = None

    @staticmethod
    def sizeHint(wr: float, hr: float) -> QSize or None:
        if Desktop.DESKTOP_SIZE is not None:
            ds = Desktop.DESKTOP_SIZE
            return QSize(int(ds.width() * wr), int(ds.height() * hr))
        return None

    @staticmethod
    def getDesktopSize() -> QSize:
        return Desktop.DESKTOP_SIZE

    @staticmethod
    def setDesktopSize(size: QSize):
        if isinstance(size, QSize):
            Desktop.DESKTOP_SIZE = size

