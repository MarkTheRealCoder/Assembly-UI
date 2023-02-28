import json
import os
if os.name == "nt":
    import win32api
    import win32con
from typing import Any, Literal

from PyQt5.QtCore import QUrl, QObject, pyqtSignal
from PyQt5.QtGui import QDesktopServices


SCALE = lambda x, y: int(x/1200*y)
SCALEH = lambda x, y: int(x/650*y)


def find_path(file: str) -> str:
    location = os.getcwd()
    result: str = ""
    for root, dir, files in os.walk(location):
        if file in files:
            result = os.path.join(root, file)
            break
    return result


def find_dir(directory: str) -> str:
    location = os.getcwd()
    result: str = ""
    for root, directories, files in os.walk(location):
        if directory in directories:
            result = os.path.join(root, directory)
            break
    return result


def openDir(path: str):
    QDesktopServices.openUrl(QUrl.fromLocalFile(path))


def is_file_hidden(file: str, path: str) -> bool:
    if os.name == 'nt':

        try:
            attribute = win32api.GetFileAttributes(path)
            return attribute & (win32con.FILE_ATTRIBUTE_HIDDEN | win32con.FILE_ATTRIBUTE_SYSTEM)
        except Exception as e:
            del e
            return False

    return file.startswith(".")


def filter_files(file_list: list[str], path: str, ext: tuple = ()) -> list[str]:
    returns: list[str] = []
    for file in file_list:
        if not file.startswith("$") and not is_file_hidden(file, path + file):
            extension = ""
            try:
                extension: str = file.rsplit(".", 2)[1]
            except Exception as e:
                del e
            if extension == "" and os.path.isdir(path + file) or (ext != () and extension in ext):
                returns.append(file)
    return returns


def ls(path: str, ext: tuple = ()):
    results: dict[str: bool] = {}
    try:
        path, dirnames, filenames = next(os.walk(path))
    except Exception as e:
        del e
        return None
    elements: list[str] = (dirnames + filenames) if ext != () else dirnames

    separator = "\\" if os.name == "nt" else "/"

    for file in filter_files(elements, path, ext):
            temp_path = ""
            if path.endswith(separator):
                temp_path = path + file + separator
            else:
                temp_path = path + separator + file + separator
            hasDirs: bool = False
            try:
                hasDirs = filter_files(os.listdir(temp_path), temp_path, ext) != []
            except Exception as e:
                del e
            results[file] = hasDirs

    return tuple([path, results])


class Variable(QObject):
    change_content = pyqtSignal(str)

    def __init__(self, content):
        super(QObject, self).__init__()
        self.content = content

    def setContent(self, content: str):
        self.content = content
        self.change_content.emit(content)

    def getContent(self):
        return self.content


class HandleJson:
    data: dict = {}
    file_list: list[str] = []
    literals = Literal["cwd", "files"]

    def __init__(self):
        self.path = find_path("data.json")
        if HandleJson.data == {}:
            self.decodeAndGet()

    def encodeAndSave(self, section: literals, _any: Any):
        if _any is None:
            return
        if section == "cwd":
            HandleJson.data[section] = _any
        if section == "files":
            HandleJson.file_list.append(_any)
            HandleJson.data[section] = HandleJson.file_list

        encoding = json.dumps(HandleJson.data)
        with open(self.path, "w") as f:
            f.write(encoding)

    def decodeAndGet(self):
        try:
            decoding = open(self.path, "r").read()
            decoding = json.loads(decoding)
            if decoding is not None:
                HandleJson.data = decoding
        except Exception as e:
            del e

    def get(self, section: literals):
        return self.data.get(section)





