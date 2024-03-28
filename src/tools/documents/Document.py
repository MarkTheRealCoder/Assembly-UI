import os
import re


class Document:
    ROOT = "C:" if os.name == "nt" else "/"
    SEP = "\\" if os.name == "nt" else "/"

    def __init__(self, path: str):
        self.___path: str = path
        self.___name: str = "name"
        self.___extension: str = "extension"
        self.___folder: str = "folder"
        self.text: str = ""

        self.___fill_data(path)
        self.___setText()

    def ___fill_data(self, path: str):
        match = re.match(fr"(?P<folder>{Document.ROOT}.*){Document.SEP}(?P<name>[A-Za-z0-9_]+)\.(?P<extension>[A-Za-z0-9.]+)", path)
        self.___name = match.group(self.___name)
        self.___folder = match.group(self.___folder)
        self.___extension = match.group(self.___extension)

    def ___setText(self, text: str = None):
        if text is None:
            with open(self.___path) as f:
                text = f.read()
        super().__setattr__("text", text)

    def __setattr__(self, key, value):
        if key == "text":
            raise Exception("Access denied. Use the proper function to accomplish this action.")
        super().__setattr__(key, value)

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

    def setText(self, text: str):
        self.___setText(text)

    def getPath(self):
        return self.___path

    def getName(self):
        return self.___name

    def getFolder(self):
        return self.___folder

    def getExtension(self):
        return self.___extension


