from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import QColor, QFont

from .Asm8088Lexer import Asm8088Lexer
from .IJVMLexer import IJVMLexer


class LexerFactory:
    """Factory class to create appropriate lexers based on file type or content"""
    
    @staticmethod
    def createLexer(parent: QsciScintilla, ext: str):
        """
        Create an appropriate lexer based on file extension
        
        Args:
            parent: The QsciScintilla parent widget
            ext: The file extension
            
        Returns:
            Appropriate lexer instance (Asm8088Lexer, IJVMLexer, or DefaultLexer)
        """
        
        # Get current document from Database
        if ext == 'a8088':
            return Asm8088Lexer(parent)
        elif ext == 'ijvm':
            return IJVMLexer(parent)
        
        # Default lexer if no specific match
        return DefaultLexer(parent)


class DefaultLexer(QsciLexerCustom):
    """Default lexer for unknown file types"""
    
    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)
        self._parent: QsciScintilla = self.parent()
        self.setDefaultPaper(QColor("#1E1E1E"))
        self.setDefaultColor(QColor("#CCCCCC"))
        self.setDefaultFont(QFont("Monospace", 12))

    def styleText(self, start, end):
        # Simple styling - just use default
        if self._parent:
            text = self._parent.text()[start:end]
            self.startStyling(start)
            self.setStyling(len(text), 0)

    def description(self, style):
        return "Default text lexer"

    def language(self):
        return "Text"


# Backward compatibility - maintain the original Lexer class
class Lexer(DefaultLexer):
    """
    Legacy Lexer class for backward compatibility
    This will be the default lexer used when no specific file type is detected
    """
    
    def __init__(self, parent: QsciScintilla = None):
        super().__init__(parent)

    def description(self, style):
        return "Assembly language lexer for Assembly-Stdio"

    def language(self):
        return "Assembly"
