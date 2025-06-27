# from PyQt5.QtWebChannel import QWebChannel
# from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
# from PyQt5.QtWidgets import QSizePolicy
#
#
# class Renderer(QWebEngineView):
#     def __init__(self, parent, file: str):
#         QWebEngineView.__init__(self, parent)
#         self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
#         self.page().setWebChannel(QWebChannel(self.page()))
#         with open(file, 'r', encoding="utf-8") as instructions:
#             self.setHtml(instructions.read())
#         self.page().webChannel().registerObject("Renderer", self)
#         self.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)


import webbrowser

from PyQt5.QtCore import QUrl
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage
from PyQt5.QtWidgets import QSizePolicy


class CustomWebEnginePage(QWebEnginePage):
    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url: QUrl, nav_type: QWebEnginePage.NavigationType, is_main_frame):
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked:
            webbrowser.open(url.toString())
            return False  # Prevent the web engine from navigating to the URL
        return True

    def createStandardContextMenu(self):
        return None


class Renderer(QWebEngineView):
    def __init__(self, parent, file: str):
        QWebEngineView.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        # Usa la pagina personalizzata
        custom_page = CustomWebEnginePage(self)
        self.setPage(custom_page)

        self.page().setWebChannel(QWebChannel(self.page()))
        with open(file, 'r', encoding="utf-8") as instructions:
            self.setHtml(instructions.read())
        self.page().webChannel().registerObject("Renderer", self)
        self.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)
