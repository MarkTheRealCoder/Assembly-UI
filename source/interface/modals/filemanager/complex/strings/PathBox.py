from source.filesystem.documents.Document import Document
from source.interface.modals.filemanager.complex.strings.TextBox import TextBox


class PathBox(TextBox):
    def __init__(self, parent):
        super().__init__(parent)

        self.setText(Document.SEP)
        self.setReadOnly(True)


