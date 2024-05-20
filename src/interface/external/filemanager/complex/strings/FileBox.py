from src.interface.external.filemanager.complex.strings.TextBox import TextBox


class FileBox(TextBox):
    def __init__(self, parent, name: str = "NewFile"):
        super().__init__(parent)

        self.setText(name)



