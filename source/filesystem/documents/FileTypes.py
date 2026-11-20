class Filetypes:

    def __init__(self, v0: int, v1: str, *aliases: str):
        self.___numeric: int = v0
        self.___extension: str = v1
        self.extensions = (v1, *aliases)

    def __eq__(self, other):
        if isinstance(other, Filetypes):
            return self.___numeric == other.___numeric and self.___extension == other.___extension
        elif isinstance(other, int):
            return self.___numeric == other
        elif isinstance(other, str):
            return self.___extension == other
        return False

    def __int__(self):
        return self.___numeric

    def __str__(self):
        return self.___extension

    def __hash__(self):
        return hash((self.___numeric, self.___extension))


class FT(Filetypes):
    FFOLD: Filetypes = Filetypes(0, "")
    FIJVM: Filetypes = Filetypes(1, "ijvm", "jas")
    F8088: Filetypes = Filetypes(2, "a8088", "asm")
    SOURCE_EXTENSIONS = F8088.extensions + FIJVM.extensions
    _TYPES = (FFOLD, FIJVM, F8088)

    @staticmethod
    def findByExt(ext: str) -> Filetypes:
        ext = ext.lower()
        for file_type in FT._TYPES:
            if ext in file_type.extensions:
                return file_type

    @staticmethod
    def findById(num: int) -> Filetypes:
        for file_type in FT._TYPES:
            if int(file_type) == num:
                return file_type

