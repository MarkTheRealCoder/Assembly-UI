import os
import re
import threading


class Document:
    SEP = "\\" if os.name == "nt" else "/"
    ___SEP = r"\\" if os.name == "nt" else "/"

    def __init__(self, path: str):
        self.___path: str = path
        self.___name: str = "name"
        self.___extension: str = "extension"
        self.___folder: str = "folder"
        self.___text: str = ""

        self.___sem = threading.Semaphore(1)

        self.___fill_data(path)
        self.___setText()

    def ___fill_data(self, path: str):
        match = re.match(fr"(?P<folder>.*){Document.___SEP}(?P<name>[A-Za-z0-9_]+)\.(?P<extension>[A-Za-z0-9.]+)", path)
        self.___name = match.group(self.___name)
        self.___folder = match.group(self.___folder)
        self.___extension = match.group(self.___extension)

    def ___setText(self):
        self.___sem.acquire()
        with open(self.___path, "r", newline="\n") as f:
            self.___text = f.read()
        self.___sem.release()

    @property
    def text(self):
        return self.___text

    @text.setter
    def text(self, text: str):
        if not isinstance(text, str):
            raise TypeError("Text value must be a string")
        self.___sem.acquire()
        self.___text = text
        with open(self.___path, "w", newline="\n") as f:
            f.write(text)
        self.___sem.release()

    @text.getter
    def text(self):
        text = self.___text
        self.___sem.acquire()
        with open(self.___path, "w", newline="\n") as f:
            f.write(text)
        self.___sem.release()
        return text

    def __dict__(self):
        return {
            "path": self.___path,
            "name": self.___name,
            "folder": self.___folder,
            "extension": self.___extension,
            "text": self.text
        }

    def __str__(self):
        return f"{self.___name}.{self.___extension}"

    def __format__(self, format_spec: str):
        if format_spec.startswith("sub"):
            return self.___path.removeprefix(format_spec.removeprefix("sub:"))
        return str(self)

    def getPath(self):
        return self.___path

    def getName(self):
        return self.___name

    def getFolder(self):
        return self.___folder

    def getExtension(self):
        return self.___extension

    def getLastModified(self):
        return os.path.getmtime(self.___path)

    def reload(self):
        self.___setText()

