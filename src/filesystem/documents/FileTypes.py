class Filetypes:

    def __init__(self, v0: int, v1: str):
        self.___numeric: int = v0
        self.___extension: str = v1

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
    FIJVM: Filetypes = Filetypes(1, "ijvm")
    F8088: Filetypes = Filetypes(2, "a8088")

    @staticmethod
    def findByExt(ext: str) -> Filetypes:
        for i in [ft for ft in dir(FT) if ft.startswith("F")]:
            attr = getattr(FT, i)
            if attr == ext:
                return attr

    @staticmethod
    def findById(num: int) -> Filetypes:
        for i in [ft for ft in dir(FT) if ft.startswith("F")]:
            attr = getattr(FT, i)
            if int(attr) == num:
                return attr

