import re

from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import QColor, QFont

from source.interface.assets import editorFont

from .Completion import CompletionSource
from .Styling import Utf8Styling


class IJVMLexer(Utf8Styling, CompletionSource, QsciLexerCustom):
    """Syntax highlighter and autocompletion source for IJVM files"""

    Default = 0
    BlockKeyword = 1
    Instruction = 2
    Number = 3
    Identifier = 4
    Comment = 5
    Symbol = 6
    Label = 7

    ___ID = r"[A-Za-z_][A-Za-z0-9_\-]*"
    ___LABEL = re.compile(rf"^\s*({___ID})\s*:")
    ___METHOD = re.compile(rf"^\s*\.method\s+({___ID})\s*(?:\((.*)\))?")
    ___FIRST = re.compile(rf"^\s*({___ID})")

    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        self._parent: QsciScintilla = self.parent()
        self.setupStyles()
        self.setupKeywords()
        self.setupCompletion(self.instructions.union(self.blockKeywords))

    def collectSymbols(self, lines: list[str]) -> set:
        """Labels, methods and their parameters, and the names declared in .var and .constant blocks"""
        symbols = set()
        block = None
        ident = re.compile(self.___ID)
        for line in lines:
            word = line.strip()
            if word in ('.var', '.constant'):
                block = word
                continue
            if word in ('.end-var', '.end-constant'):
                block = None
                continue
            if block is not None:
                if match := self.___FIRST.match(line):
                    symbols.add(match.group(1))
                continue
            if match := self.___METHOD.match(line):
                symbols.add(match.group(1))
                if match.group(2):
                    symbols.update(ident.findall(match.group(2)))
            elif match := self.___LABEL.match(line):
                symbols.add(match.group(1))
        return symbols

    def autoCompletionWordSeparators(self):
        return [",", " ", "\t", "(", ")", "[", "]", "{", "}", ":", ";", "+", "-", "*", "/", "=", "<", ">", "!", "&", "|", "^", "%", "~", "\"", "'"]

    def wordCharacters(self):
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.-"

    def setupStyles(self):
        self.setDefaultFont(editorFont())
        self.setDefaultColor(QColor("#CCCCCC"))
        self.setDefaultPaper(QColor("#292727"))

        # Block keyword style (.constant, .main, etc.)
        self.setColor(QColor("#569CD6"), self.BlockKeyword)
        self.setFont(editorFont(weight=QFont.DemiBold), self.BlockKeyword)

        # Instruction style (HALT, IADD, etc.)
        self.setColor(QColor("#4EC9B0"), self.Instruction)
        self.setFont(editorFont(weight=QFont.DemiBold), self.Instruction)

        self.setColor(QColor("#B5CEA8"), self.Number)
        self.setFont(editorFont(), self.Number)

        self.setColor(QColor("#9CDCFE"), self.Identifier)
        self.setFont(editorFont(), self.Identifier)

        self.setColor(QColor("#6A9955"), self.Comment)
        self.setFont(editorFont(italic=True), self.Comment)

        self.setColor(QColor("#D4D4D4"), self.Symbol)
        self.setFont(editorFont(), self.Symbol)

        self.setColor(QColor("#DCDCAA"), self.Label)
        self.setFont(editorFont(weight=QFont.DemiBold), self.Label)

    def setupKeywords(self):
        self.blockKeywords = {
            '.constant', '.end-constant', '.main', '.end-main',
            '.method', '.end-method', '.var', '.end-var'
        }

        self.instructions = {
            'HALT', 'NOP', 'IADD', 'IAND', 'IOR', 'ISUB', 'POP', 'SWAP',
            'DUP', 'ERR', 'IN', 'OUT', 'IRETURN', 'BIPUSH', 'IINC',
            'ILOAD', 'ISTORE', 'INVOKEVIRTUAL', 'LDC_W', 'IFLT', 'IFEQ',
            'IF_ICMPEQ', 'GOTO',
            'halt', 'nop', 'iadd', 'iand', 'ior', 'isub', 'pop', 'swap',
            'dup', 'err', 'in', 'out', 'ireturn', 'bipush', 'iinc',
            'iload', 'istore', 'invokevirtual', 'ldc_w', 'iflt', 'ifeq',
            'if_icmpeq', 'goto'
        }

    def styleText(self, start, end):
        if not self._parent:
            return

        text = self.beginStyling(start, end)
        
        i = 0
        while i < len(text):
            char = text[i]
            
            if char.isspace():
                self.setStyling(1, self.Default)
                i += 1
                continue
            
            # Handle comments (// or ;)
            if i < len(text) - 1 and text[i:i+2] == '//':
                comment_end = text.find('\n', i)
                if comment_end == -1:
                    comment_end = len(text)
                comment_length = comment_end - i
                self.setStyling(comment_length, self.Comment)
                i = comment_end
                continue
            elif char == ';':
                comment_end = text.find('\n', i)
                if comment_end == -1:
                    comment_end = len(text)
                comment_length = comment_end - i
                self.setStyling(comment_length, self.Comment)
                i = comment_end
                continue
            
            # Handle numbers (hex, octal, decimal)
            if char.isdigit() or (char == '0' and i < len(text) - 1 and text[i+1].lower() in 'xo') or (char == '-' and i < len(text) - 1 and text[i+1].isdigit()):
                number_start = i
                if char == '-':
                    i += 1
                if i < len(text) and text[i] == '0' and i < len(text) - 1:
                    if text[i+1].lower() == 'x':
                        i += 2
                        while i < len(text) and text[i].lower() in '0123456789abcdef':
                            i += 1
                    elif text[i+1].lower() == 'o':
                        i += 2
                        while i < len(text) and text[i] in '01234567':
                            i += 1
                    else:
                        while i < len(text) and text[i].isdigit():
                            i += 1
                else:
                    while i < len(text) and text[i].isdigit():
                        i += 1
                number_length = i - number_start
                self.setStyling(number_length, self.Number)
                continue
            
            # Handle identifiers, block keywords, instructions
            if char.isalpha() or char == '_' or char == '.':
                word_start = i
                
                while i < len(text) and (text[i].isalnum() or text[i] in '_.-'):
                    i += 1
                
                word = text[word_start:i]
                word_length = i - word_start
                
                # Check if next character is colon (label)
                if i < len(text) and text[i] == ':':
                    i += 1
                    word_length += 1
                    self.setStyling(word_length, self.Label)
                    continue
                
                if word in self.blockKeywords:
                    self.setStyling(word_length, self.BlockKeyword)
                elif word in self.instructions:
                    self.setStyling(word_length, self.Instruction)
                else:
                    self.setStyling(word_length, self.Identifier)
                continue
            
            # Handle symbols
            if char in '(),:-':
                self.setStyling(1, self.Symbol)
                i += 1
                continue
            
            self.setStyling(1, self.Default)
            i += 1

    def description(self, style):
        descriptions = {
            self.Default: "Default",
            self.BlockKeyword: "Block Keyword",
            self.Instruction: "Instruction",
            self.Number: "Number",
            self.Identifier: "Identifier",
            self.Comment: "Comment",
            self.Symbol: "Symbol",
            self.Label: "Label"
        }
        return descriptions.get(style, "Unknown")

    def language(self):
        return "IJVM"

    def keywords(self, set_num):
        if set_num == 1:
            return " ".join(self.instructions)
        elif set_num == 2:
            return " ".join(self.blockKeywords)
        return "" 