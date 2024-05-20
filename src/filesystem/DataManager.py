import json
from typing import Any, Literal

from PyQt5.QtCore import QObject

from src.eventhandlers.Register import EventRegister
from src.events.data.ClosingEvent import ClosingEvent
from src.filesystem.Folder import find_path
from src.signals.Variables import DataBase


def _open(mode: str = "r") -> Any:
    def wrapper(func):
        path = find_path("data.json")

        def inner(*args, **kwargs):
            nonlocal path, mode
            with open(path, mode) as file:
                args = (args[0], file)
                return func(*args, **kwargs)

        return inner

    return wrapper


@EventRegister.register(ClosingEvent, priority=EventRegister.URGENT)
class HandleJson(QObject):
    __slots__ = "___data"
    ___AVAILABLE_SAVINGS = Literal["cwd", "font", "files"]
    ___SINGLETON = None

    @_open(mode="r")
    def ___decode(self, file):
        data = {}
        try:
            data = json.load(file)
        except json.JSONDecodeError:
            pass
        return data

    def __init__(self):
        super().__init__()
        self.___data = self.___decode()

        DataBase.FOLDER.connect(self.set_cwd)
        DataBase.FONT.connect(self.set_font)

    def event(self, event):
        if event == ClosingEvent:
            self.___encode()
        return super().event(event)

    @_open(mode="r+")
    def ___encode(self, file):
        encoding = json.dumps(self.___data, indent=4, sort_keys=True)
        file.truncate()
        file.write(encoding)

    def get(self, key: ___AVAILABLE_SAVINGS):
        return self.___data.get(key, None)

    def set_cwd(self):
        self.___data["cwd"] = DataBase.FOLDER.getValue()

    def set_font(self):
        self.___data["font"] = DataBase.FONT.getValue()

    def set_files(self, files: list[str]):
        self.___data["files"] = files

    def get_cwd(self):
        DataBase.FOLDER.setValue(folder if (folder := self.get("cwd")) is not None else "")

    def get_font(self):
        DataBase.FONT.setValue(font if (font := self.get("font")) is not None else "Fira Code")

    def get_files(self):
        return files if (files := self.get("files")) is not None else []

    @staticmethod
    def get_instance():
        if HandleJson.___SINGLETON is None:
            HandleJson.___SINGLETON = HandleJson()
        return HandleJson.___SINGLETON
