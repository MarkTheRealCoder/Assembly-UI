import os
import threading


class Document:
    SEP = "\\" if os.name == "nt" else "/"

    def __init__(self, path: str):
        self.___path: str = path
        self.___name: str = "name"
        self.___extension: str = "extension"
        self.___folder: str = "folder"
        self.___text: str = ""
        self.___encoding: str = "utf-8"

        self.___sem = threading.Semaphore(1)

        self.___fill_data(path)
        self.___setText()

    def ___fill_data(self, path: str):
        self.___folder, filename = os.path.split(path)
        self.___name, extension = os.path.splitext(filename)
        self.___extension = extension[1:]

    def ___setText(self):
        with self.___sem:
            with open(self.___path, "rb") as f:
                raw = f.read()
            # Files written by older Windows builds use the legacy ANSI code page.
            for encoding in ("utf-8", "cp1252", "latin-1"):
                try:
                    self.___text = raw.decode(encoding)
                    self.___encoding = encoding
                    break
                except UnicodeDecodeError:
                    continue

    def ___encode(self, text: str) -> bytes:
        try:
            return text.encode(self.___encoding)
        except UnicodeEncodeError:
            self.___encoding = "utf-8"
            return text.encode(self.___encoding)

    @property
    def text(self):
        return self.___text

    @text.setter
    def text(self, text: str):
        if not isinstance(text, str):
            raise TypeError("Text value must be a string")
        with self.___sem:
            data = self.___encode(text)
            with open(self.___path, "wb") as f:
                f.write(data)
            self.___text = text

    def __dict__(self):
        return {
            "path": self.___path,
            "name": self.___name,
            "folder": self.___folder,
            "extension": self.___extension,
            "text": self.text
        }

    def __repr__(self):
        return f"{self.___name}.{self.___extension}"

    def __str__(self):
        return self.___path

    def __format__(self, format_spec: str):
        if format_spec.startswith("sub"):
            return self.___path.removeprefix(format_spec.removeprefix("sub:"))
        return str(self)

    def getPath(self):
        return self.___path

    def getName(self):
        return self.___name

    def getExtension(self):
        return self.___extension

    def getLastModified(self):
        return os.path.getmtime(self.___path)

    def reload(self):
        self.___setText()

