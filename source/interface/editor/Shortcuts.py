from PyQt5.QtWidgets import QApplication


def ctrlx(editor, event):
    if not editor.hasSelectedText():
        line = editor.getCursorPosition()[0]
        text = editor.text(line)
        editor.setSelection(line, 0, line+1, 0)
        editor.removeSelectedText()
        clipboard = QApplication.clipboard()
        if text != "":
            clipboard.setText(text)
        return True
    return None
