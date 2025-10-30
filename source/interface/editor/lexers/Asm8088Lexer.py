from PyQt5.Qsci import QsciLexerCustom, QsciScintilla, QsciAPIs
from PyQt5.QtGui import QColor, QFont


class Asm8088Lexer(QsciLexerCustom):
    # Style constants
    Default = 0
    Directive = 1
    Instruction = 2
    Register = 3
    Number = 4
    Identifier = 5
    Comment = 6
    String = 7
    Symbol = 8
    Label = 9

    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        self._parent: QsciScintilla = self.parent()
        self.setupStyles()
        self.setupKeywords()
        self.___apis = QsciAPIs(self)
        for api in self.instructions.union(self.registers).union(self.directives):
            self.___apis.add(api)
        self.___apis.prepare()
        self.setAPIs(self.___apis)

    def autoCompletionWordSeparators(self):
        return [",", " ", "\t", "(", ")", "[", "]", "{", "}", ":", ";", "+", "-", "*", "/", "=", "<", ">", "!", "&", "|", "^", "%", "~", "\"", "'"]

    def wordCharacters(self):
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_."

    def setupStyles(self):
        # Default style
        self.setDefaultFont(QFont("Bahnschrift", 12))
        self.setDefaultColor(QColor("#CCCCCC"))
        self.setDefaultPaper(QColor("#292727"))

        # Directive style (.SECT, .BYTE, etc.)
        self.setColor(QColor("#569CD6"), self.Directive)
        self.setFont(QFont("Bahnschrift", 12, weight=63), self.Directive)

        # Instruction style (MOV, ADD, etc.)
        self.setColor(QColor("#4EC9B0"), self.Instruction)
        self.setFont(QFont("Bahnschrift", 12, weight=63), self.Instruction)

        # Register style (AX, BX, etc.)
        self.setColor(QColor("#FFC83D"), self.Register)
        self.setFont(QFont("Bahnschrift", 12), self.Register)

        # Number style
        self.setColor(QColor("#B5CEA8"), self.Number)
        self.setFont(QFont("Bahnschrift", 12), self.Number)

        # Identifier style
        self.setColor(QColor("#9CDCFE"), self.Identifier)
        self.setFont(QFont("Bahnschrift", 12), self.Identifier)

        # Comment style
        self.setColor(QColor("#6A9955"), self.Comment)
        self.setFont(QFont("Bahnschrift", 12, italic=True), self.Comment)

        # String style
        self.setColor(QColor("#CE9178"), self.String)
        self.setFont(QFont("Bahnschrift", 12), self.String)

        # Symbol style
        self.setColor(QColor("#D4D4D4"), self.Symbol)
        self.setFont(QFont("Bahnschrift", 12), self.Symbol)

        # Label style
        self.setColor(QColor("#DCDCAA"), self.Label)
        self.setFont(QFont("Bahnschrift", 12, weight=63), self.Label)

    def setupKeywords(self):
        # Directives
        self.directives = {
            '.SECT', '.BYTE', '.ASCII', '.SPACE', '.DATA', '.TEXT', '.BSS',
            '.sect', '.byte', '.ascii', '.space', '.data', '.text', '.bss'
        }

        # Instructions
        self.instructions = {
            'MOV', 'PUSH', 'POP', 'ADD', 'ADC', 'SUB', 'SBB', 'MUL', 'DIV',
            'INC', 'DEC', 'CMP', 'AND', 'OR', 'XOR', 'NOT', 'JMP', 'JE', 'JZ',
            'JNE', 'JNZ', 'JL', 'JNGE', 'JLE', 'JNG', 'JG', 'JNLE', 'JGE',
            'JNL', 'JB', 'JNAE', 'JBE', 'JNA', 'JA', 'JNBE', 'JAE', 'JNB',
            'JS', 'JNS', 'JO', 'JNO', 'JP', 'JPE', 'JNP', 'JPO', 'JC', 'JNC',
            'JCXZ', 'LOOP', 'CALL', 'RET', 'MOVB', 'SUBB', 'DIVB', 'CMPB',
            'ADDB', 'XORB', 'MULB', 'SYS',
            'mov', 'push', 'pop', 'add', 'adc', 'sub', 'sbb', 'mul', 'div',
            'inc', 'dec', 'cmp', 'and', 'or', 'xor', 'not', 'jmp', 'je', 'jz',
            'jne', 'jnz', 'jl', 'jnge', 'jle', 'jng', 'jg', 'jnle', 'jge',
            'jnl', 'jb', 'jnae', 'jbe', 'jna', 'ja', 'jnbe', 'jae', 'jnb',
            'js', 'jns', 'jo', 'jno', 'jp', 'jpe', 'jnp', 'jpo', 'jc', 'jnc',
            'jcxz', 'loop', 'call', 'ret', 'movb', 'subb', 'divb', 'cmpb',
            'addb', 'xorb', 'mulb', 'sys'
        }

        # Registers
        self.registers = {
            'AX', 'BX', 'CX', 'DX', 'SI', 'DI', 'BP', 'SP',
            'AL', 'AH', 'BL', 'BH', 'CL', 'CH', 'DL', 'DH',
            'CS', 'DS', 'ES', 'SS',
            'ax', 'bx', 'cx', 'dx', 'si', 'di', 'bp', 'sp',
            'al', 'ah', 'bl', 'bh', 'cl', 'ch', 'dl', 'dh',
            'cs', 'ds', 'es', 'ss'
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
            
            # Handle string literals
            if char == '"':
                string_start = i
                i += 1
                while i < len(text) and text[i] != '"':
                    i += 1
                if i < len(text):
                    i += 1  # Include closing quote
                string_length = i - string_start
                self.setStyling(string_length, self.String)
                continue
            
            # Handle numbers (hex and decimal)
            if char.isdigit() or (char == '0' and i < len(text) - 1 and text[i+1].lower() == 'x'):
                number_start = i
                if char == '0' and i < len(text) - 1 and text[i+1].lower() == 'x':
                    # Hexadecimal
                    i += 2  # Skip 0x
                    while i < len(text) and text[i].lower() in '0123456789abcdef':
                        i += 1
                else:
                    # Decimal (possibly negative)
                    if char == '-':
                        i += 1
                    while i < len(text) and text[i].isdigit():
                        i += 1
                number_length = i - number_start
                self.setStyling(number_length, self.Number)
                continue
            
            # Handle identifiers, directives, instructions, registers
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
                if word in self.directives:
                    self.setStyling(word_length, self.Directive)
                elif word in self.instructions:
                    self.setStyling(word_length, self.Instruction)
                elif word in self.registers:
                    self.setStyling(word_length, self.Register)
                else:
                    self.setStyling(word_length, self.Identifier)
                continue
            
            # Handle symbols
            if char in '=:,()[]+-':
                self.setStyling(1, self.Symbol)
                i += 1
                continue
            
            # Default for any other character
            self.setStyling(1, self.Default)
            i += 1

    def description(self, style):
        descriptions = {
            self.Default: "Default",
            self.Directive: "Directive",
            self.Instruction: "Instruction", 
            self.Register: "Register",
            self.Number: "Number",
            self.Identifier: "Identifier",
            self.Comment: "Comment",
            self.String: "String",
            self.Symbol: "Symbol",
            self.Label: "Label"
        }
        return descriptions.get(style, "Unknown")

    def language(self):
        return "8088 Assembly"

    def keywords(self, set_num):
        if set_num == 1:
            return " ".join(self.instructions)
        elif set_num == 2:
            return " ".join(self.registers)
        elif set_num == 3:
            return " ".join(self.directives)
        return "" 