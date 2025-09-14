from PyQt5.Qsci import QsciLexerCustom, QsciScintilla
from PyQt5.QtGui import QColor, QFont

from source.comms import Database
from .Asm8088Lexer import Asm8088Lexer
from .IJVMLexer import IJVMLexer


class LexerFactory:
    """Factory class to create appropriate lexers based on file type or content"""
    
    @staticmethod
    def createLexer(parent: QsciScintilla, content: str = None):
        """
        Create an appropriate lexer based on current file extension or content
        
        Args:
            parent: The QsciScintilla parent widget
            content: Optional content to analyze for lexer selection
            
        Returns:
            Appropriate lexer instance (Asm8088Lexer, IJVMLexer, or DefaultLexer)
        """
        
        # Get current document from Database
        current_document = Database.CURRENT_FILE.getValue()
        
        # Determine lexer type from file extension
        if current_document:
            file_ext = current_document.getExtension().lower()
            if file_ext in ['asm', 's', 'a8088', '8088']:
                return Asm8088Lexer(parent)
            elif file_ext in ['ijvm', 'jvm']:
                return IJVMLexer(parent)
        
        # Determine lexer type from content analysis
        if content:
            content_lower = content.lower()
            
            # Check for IJVM-specific keywords
            ijvm_keywords = ['.constant', '.main', '.method', '.var', 'halt', 'iadd', 'bipush']
            if any(keyword in content_lower for keyword in ijvm_keywords):
                return IJVMLexer(parent)
            
            # Check for 8088-specific keywords
            asm8088_keywords = ['.sect', '.data', '.text', '.bss', 'mov', 'push', 'pop', 'jmp']
            if any(keyword in content_lower for keyword in asm8088_keywords):
                return Asm8088Lexer(parent)
        
        # Default to 8088 assembly lexer if no specific match
        return Asm8088Lexer(parent)


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
