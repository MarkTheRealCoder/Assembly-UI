from source.interface.templates import GenericButton


class ColorButtonGraphics(GenericButton):
    def __init__(self, parent):
        super().__init__(parent)
        self.setObjectName("CPColorDialogButton")


class ColorButtonLogic(ColorButtonGraphics):
    def __init__(self, parent):
        super().__init__(parent)


class ColorButton(ColorButtonLogic):
    def __init__(self, parent):
        super().__init__(parent)