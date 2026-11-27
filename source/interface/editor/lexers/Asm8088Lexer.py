import re

from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import QColor, QFont

from source.interface.assets import editorFont

from .Completion import CompletionSource
from .Styling import Utf8Styling


class Asm8088Lexer(Utf8Styling, CompletionSource, QsciLexerCustom):
    """Syntax highlighter and autocompletion source for 8088 assembly files"""

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

    STRINGS = True
    ___LABEL = re.compile(r"([A-Za-z_][A-Za-z0-9_]*)\s*:")
    ___CONSTANT = re.compile(r"^\s*([A-Za-z_][A-Za-z0-9_]*)\s*=")

    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        self._parent: QsciScintilla = self.parent()
        self.setupStyles()
        self.setupKeywords()
        self.setupCompletion(self.instructions.union(self.registers).union(self.directives))

    def collectSymbols(self, lines: list[str]) -> set:
        """Labels (name:), also of data such as 'msg: .ASCII', and constants (NAME = value)"""
        symbols = set()
        for line in lines:
            if match := self.___CONSTANT.match(line):
                symbols.add(match.group(1))
            rest = line
            # A line can start with several labels, as in 'a: b: MOV AX, 1'.
            while match := self.___LABEL.match(rest.lstrip()):
                symbols.add(match.group(1))
                rest = rest.lstrip()[match.end():]
        return symbols

    def autoCompletionWordSeparators(self):
        return [",", " ", "\t", "(", ")", "[", "]", "{", "}", ":", ";", "+", "-", "*", "/", "=", "<", ">", "!", "&", "|", "^", "%", "~", "\"", "'"]

    def wordCharacters(self):
        return "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_."

    def setupStyles(self):
        self.setDefaultFont(editorFont())
        self.setDefaultColor(QColor("#CCCCCC"))
        self.setDefaultPaper(QColor("#292727"))

        # Directive style (.SECT, .BYTE, etc.)
        self.setColor(QColor("#569CD6"), self.Directive)
        self.setFont(editorFont(weight=QFont.DemiBold), self.Directive)

        # Instruction style (MOV, ADD, etc.)
        self.setColor(QColor("#4EC9B0"), self.Instruction)
        self.setFont(editorFont(weight=QFont.DemiBold), self.Instruction)

        # Register style (AX, BX, etc.)
        self.setColor(QColor("#FFC83D"), self.Register)
        self.setFont(editorFont(), self.Register)

        self.setColor(QColor("#B5CEA8"), self.Number)
        self.setFont(editorFont(), self.Number)

        self.setColor(QColor("#9CDCFE"), self.Identifier)
        self.setFont(editorFont(), self.Identifier)

        self.setColor(QColor("#6A9955"), self.Comment)
        self.setFont(editorFont(italic=True), self.Comment)

        # String style
        self.setColor(QColor("#CE9178"), self.String)
        self.setFont(editorFont(), self.String)

        self.setColor(QColor("#D4D4D4"), self.Symbol)
        self.setFont(editorFont(), self.Symbol)

        self.setColor(QColor("#DCDCAA"), self.Label)
        self.setFont(editorFont(weight=QFont.DemiBold), self.Label)

    def setupKeywords(self):
        self.directives = {
            '.SECT', '.BYTE', '.ASCII', '.SPACE', '.DATA', '.TEXT', '.BSS',
            '.sect', '.byte', '.ascii', '.space', '.data', '.text', '.bss'
        }

        self.instructions = {
            'MOV', 'PUSH', 'POP', 'ADD', 'ADC', 'SUB', 'SBB', 'MUL', 'DIV',
            'INC', 'DEC', 'CMP', 'AND', 'OR', 'XOR', 'NOT', 'JMP', 'JE', 'JZ',
            'JNE', 'JNZ', 'JL', 'JNGE', 'JLE', 'JNG', 'JG', 'JNLE', 'JGE',
            'JNL', 'JB', 'JNAE', 'JBE', 'JNA', 'JA', 'JNBE', 'JAE', 'JNB',
            'JS', 'JNS', 'JO', 'JNO', 'JP', 'JPE', 'JNP', 'JPO', 'JC', 'JNC',
            'JCXZ', 'LOOP', 'CALL', 'RET', 'MOVB', 'SUBB', 'DIVB', 'CMPB',
            'ADDB', 'XORB', 'MULB', 'SYS', 'HLT', 'NOP',
            'mov', 'push', 'pop', 'add', 'adc', 'sub', 'sbb', 'mul', 'div',
            'inc', 'dec', 'cmp', 'and', 'or', 'xor', 'not', 'jmp', 'je', 'jz',
            'jne', 'jnz', 'jl', 'jnge', 'jle', 'jng', 'jg', 'jnle', 'jge',
            'jnl', 'jb', 'jnae', 'jbe', 'jna', 'ja', 'jnbe', 'jae', 'jnb',
            'js', 'jns', 'jo', 'jno', 'jp', 'jpe', 'jnp', 'jpo', 'jc', 'jnc',
            'jcxz', 'loop', 'call', 'ret', 'movb', 'subb', 'divb', 'cmpb',
            'addb', 'xorb', 'mulb', 'sys', 'hlt', 'nop'
        }

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
                    i += 2
                    while i < len(text) and text[i].lower() in '0123456789abcdef':
                        i += 1
                else:
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