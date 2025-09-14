from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QSizePolicy

from source.interface.shared import createLayout


class SettingsGraphics(QWidget):
    def __init__(self, parent):
        super().__init__(parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setupUI()

    def setupUI(self):
        layout: QVBoxLayout = createLayout(QVBoxLayout, self)
        
        # Font Settings Section
        font_section = self.createFontSection()
        layout.addWidget(font_section)
        
        # Display Settings Section
        display_section = self.createDisplaySection()
        layout.addWidget(display_section)
        
        # Editor Settings Section
        editor_section = self.createEditorSection()
        layout.addWidget(editor_section)
        
        self.setLayout(layout)

    def createFontSection(self):
        section = QLabel("Font Settings")
        section.setObjectName("SettingsSection")
        return section

    def createDisplaySection(self):
        section = QLabel("Display Settings")
        section.setObjectName("SettingsSection")
        return section

    def createEditorSection(self):
        section = QLabel("Editor Settings")
        section.setObjectName("SettingsSection")
        return section


class SettingsLogic(SettingsGraphics):
    def __init__(self, parent):
        super().__init__(parent)
        self.font_family = "Anonymous Pro"
        self.font_size = 12
        self.theme = "Dark"
        self.auto_save = True
        self.line_numbers = True

    def getFontFamily(self):
        return self.font_family

    def setFontFamily(self, family: str):
        self.font_family = family

    def getFontSize(self):
        return self.font_size

    def setFontSize(self, size: int):
        self.font_size = size

    def getTheme(self):
        return self.theme

    def setTheme(self, theme: str):
        self.theme = theme

    def getAutoSave(self):
        return self.auto_save

    def setAutoSave(self, enabled: bool):
        self.auto_save = enabled

    def getLineNumbers(self):
        return self.line_numbers

    def setLineNumbers(self, enabled: bool):
        self.line_numbers = enabled


class Settings(SettingsLogic):
    def __init__(self, parent):
        super().__init__(parent)
        self.setupConnections()

    def setupConnections(self):
        # This method can be used to connect UI elements to logic methods
        # when the UI is fully implemented
        pass

    def applySettings(self):
        """Apply the current settings to the application"""
        # This method would apply the settings to the main application
        pass

    def resetToDefaults(self):
        """Reset all settings to their default values"""
        self.setFontFamily("Anonymous Pro")
        self.setFontSize(12)
        self.setTheme("Dark")
        self.setAutoSave(True)
        self.setLineNumbers(True) 

