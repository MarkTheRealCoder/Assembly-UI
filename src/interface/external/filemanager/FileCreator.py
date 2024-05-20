from src.interface.external.filemanager.complex.FileComplex import FileComplex


class FileCreator(FileComplex):
    def __init__(self):
        super().__init__(["a8088", "ijvm"])
        self.confirm.onClick(self.___confirm)

    def ___confirm(self):
        pass
