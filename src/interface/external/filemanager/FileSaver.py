from src.filesystem.documents.Document import Document
from src.interface.external.filemanager.complex.FileComplex import FileComplex
from src.signals.Variables import DataBase


class FileSaver(FileComplex):
    def __init__(self):
        self.cd: Document = DataBase.CURRENT_FILE.getValue()
        exts = ["ijvm", "jas"]
        if DataBase.DOCTYPE.getValue() == 2:
            exts = ["a8088", "s"]
        super().__init__(exts, name=self.cd.getName())
        self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        name = self.get_name()
        path = DataBase.FOLDER.getValue() + self.get_path().removeprefix(Document.SEP)
        ext = self.get_extension().lower()
        if name == "":
            return
        with open(path + name + "." + ext, "x", newline="\n") as file:
            file.write(self.cd.text)
        self.parent().deleteNow()




