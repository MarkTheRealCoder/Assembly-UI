from PyQt5.Qsci import QsciAPIs


def stripComment(line: str, strings: bool = False) -> str:
    """Return the code of a line before its ';' or '//' comment. With strings, a comment mark inside quotes is code"""
    quoted = False
    for i, char in enumerate(line):
        if strings and char == '"':
            quoted = not quoted
        elif not quoted and (char == ';' or line.startswith('//', i)):
            return line[:i]
    return line


class CompletionSource:
    """
    Completion list of a lexer: its keywords and the symbols declared in the file, such as labels and variables.
    Words written in comments are never proposed, and the list stays closed while a comment is being typed.
    """

    STRINGS = False

    def setupCompletion(self, keywords):
        self.___keywords = set(keywords)
        self.___symbols: set = None
        self.___preparing = False
        self.___dirty = False
        self.___apis = QsciAPIs(self)
        self.___apis.apiPreparationFinished.connect(self.___preparationFinished)
        self.setAPIs(self.___apis)
        self.___rebuild(set())

    def collectSymbols(self, lines: list[str]) -> set:
        """Return the symbols declared in the code lines, already stripped of their comments"""
        return set()

    def isInComment(self, prefix: str) -> bool:
        """Tell whether the cursor after the text prefix of a line is inside a comment or a string"""
        code = stripComment(prefix, self.STRINGS)
        if len(code) != len(prefix):
            return True
        return self.STRINGS and code.count('"') % 2 == 1

    def refreshCompletions(self, text: str):
        """Update the symbols of the completion list from the text of the file"""
        lines = [stripComment(line, self.STRINGS) for line in text.splitlines()]
        symbols = self.collectSymbols(lines) - self.___keywords
        if symbols != self.___symbols:
            self.___rebuild(symbols)

    def ___rebuild(self, symbols: set):
        self.___symbols = symbols
        if self.___preparing:
            # QsciAPIs ignores a preparation requested while another one runs: repeat it when that one ends.
            self.___dirty = True
            return
        self.___apis.clear()
        for word in sorted(self.___keywords | symbols):
            self.___apis.add(word)
        self.___preparing = True
        self.___apis.prepare()

    def ___preparationFinished(self):
        self.___preparing = False
        if self.___dirty:
            self.___dirty = False
            self.___rebuild(self.___symbols)
