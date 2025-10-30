from PyQt5.Qsci import QsciLexerCustom, QsciScintilla, QsciAPIs
from PyQt5.QtGui import QColor, QFont


class IJVMLexer(QsciLexerCustom):
    # Style constants
    Default = 0
    BlockKeyword = 1
    Instruction = 2
    Number = 3
    Identifier = 4
    Comment = 5
    Symbol = 6
    Label = 7

    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        self._parent: QsciScintilla = self.parent()
        self.setupStyles()
        self.setupKeywords()
        self.___apis = QsciAPIs(self)
        for api in self.instructions.union(self.blockKeywords):
            self.___apis.add(api)
        self.___apis.prepare()
        self.setAPIs(self.___apis)

    def autoCompletionWordSeparators(self):
        return [",", " ", "\t", "(", ")", "[", "]", "{", "}", ":", ";", "+", "-", "*", "/", "=", "<", ">", "!", "&", "|", "^", "%", "~", "\"", "'"]

    def wordCharacters(self):
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.-"

    def setupStyles(self):
        # Default style
        self.setDefaultFont(QFont("Bahnschrift", 12))
        self.setDefaultColor(QColor("#CCCCCC"))
        self.setDefaultPaper(QColor("#292727"))

        # Block keyword style (.constant, .main, etc.)
        self.setColor(QColor("#569CD6"), self.BlockKeyword)
        self.setFont(QFont("Bahnschrift", 12, weight=63), self.BlockKeyword)

        # Instruction style (HALT, IADD, etc.)
        self.setColor(QColor("#4EC9B0"), self.Instruction)
        self.setFont(QFont("Bahnschrift", 12, weight=63), self.Instruction)

        # Number style
        self.setColor(QColor("#B5CEA8"), self.Number)
        self.setFont(QFont("Bahnschrift", 12), self.Number)

        # Identifier style
        self.setColor(QColor("#9CDCFE"), self.Identifier)
        self.setFont(QFont("Bahnschrift", 12), self.Identifier)

        # Comment style
        self.setColor(QColor("#6A9955"), self.Comment)
        self.setFont(QFont("Bahnschrift", 12, italic=True), self.Comment)

        # Symbol style
        self.setColor(QColor("#D4D4D4"), self.Symbol)
        self.setFont(QFont("Bahnschrift", 12), self.Symbol)

        # Label style
        self.setColor(QColor("#DCDCAA"), self.Label)
        self.setFont(QFont("Bahnschrift", 12, weight=63), self.Label)

    def setupKeywords(self):
        # Block keywords
        self.blockKeywords = {
            '.constant', '.end-constant', '.main', '.end-main',
            '.method', '.end-method', '.var', '.end-var'
        }

        # Instructions
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

        # Get the text to style
        text = self._parent.text()[start:end]
        
        # Start styling from the beginning
        self.startStyling(start)
        
        # Process character by character
        i = 0
        while i < len(text):
            char = text[i]
            
            # Skip whitespace
            if char.isspace():
                self.setStyling(1, self.Default)
                i += 1
                continue
            
            # Handle comments (// or ;)
            if i < len(text) - 1 and text[i:i+2] == '//':
                # Find end of line
                comment_end = text.find('\n', i)
                if comment_end == -1:
                    comment_end = len(text)
                comment_length = comment_end - i
                self.setStyling(comment_length, self.Comment)
                i = comment_end
                continue
            elif char == ';':
                # Find end of line
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
                    i += 1  # Skip negative sign
                if i < len(text) and text[i] == '0' and i < len(text) - 1:
                    if text[i+1].lower() == 'x':
                        # Hexadecimal
                        i += 2  # Skip 0x
                        while i < len(text) and text[i].lower() in '0123456789abcdef':
                            i += 1
                    elif text[i+1].lower() == 'o':
                        # Octal
                        i += 2  # Skip 0o
                        while i < len(text) and text[i] in '01234567':
                            i += 1
                    else:
                        # Decimal starting with 0
                        while i < len(text) and text[i].isdigit():
                            i += 1
                else:
                    # Regular decimal
                    while i < len(text) and text[i].isdigit():
                        i += 1
                number_length = i - number_start
                self.setStyling(number_length, self.Number)
                continue
            
            # Handle identifiers, block keywords, instructions
            if char.isalpha() or char == '_' or char == '.':
                word_start = i
                
                # Read the complete word
                while i < len(text) and (text[i].isalnum() or text[i] in '_.-'):
                    i += 1
                
                word = text[word_start:i]
                word_length = i - word_start
                
                # Check if next character is colon (label)
                if i < len(text) and text[i] == ':':
                    # Include the colon in the label
                    i += 1
                    word_length += 1
                    self.setStyling(word_length, self.Label)
                    continue
                
                # Determine word type
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
            
            # Default for any other character
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