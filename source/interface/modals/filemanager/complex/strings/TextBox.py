from PyQt5.QtWidgets import QLineEdit, QSizePolicy


class TextBox(QLineEdit):
    def __init__(self, parent):
        super().__init__(parent)

        self.configurations()

        self.___placeholder_e = lambda x: None # Placeholder for execution

        self.textEdited.connect(lambda: self.___placeholder_e(self.text())) # Execution

    def configurations(self):
        self.setReadOnly(False)
        self.setAcceptDrops(False)
        self.setObjectName("TextBox")
        self.setMaxLength(200)
        self.setFixedHeight(30)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)

    def onEditing(self, func: callable):
        if not callable(func):
            raise TypeError("func must be callable")
        self.___placeholder_e = func


