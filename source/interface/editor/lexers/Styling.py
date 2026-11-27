class Utf8Styling:
    """
    Converts the lengths of the styled text from characters to bytes.
    Scintilla counts positions in UTF-8 bytes, while the lexers walk the text as a Python string, in characters.
    A character such as "²" or "è" takes two bytes or more: without the conversion, each one moved the styles of the
    rest of the file one byte back, so the last character of the following lines took the wrong color.
    The lexer starts with beginStyling() and then styles the text in order, with setStyling().
    """

    def beginStyling(self, start: int, end: int) -> str:
        """ Start styling the bytes from start to end and return them as text """
        self.___text = self._parent.text().encode("utf-8")[start:end].decode("utf-8", errors="replace")
        self.___cursor = 0
        self.startStyling(start)
        return self.___text

    def setStyling(self, length: int, style: int):
        """ Style the next length characters of the text """
        piece = self.___text[self.___cursor:self.___cursor + length]
        self.___cursor += length
        super().setStyling(len(piece.encode("utf-8")), style)
