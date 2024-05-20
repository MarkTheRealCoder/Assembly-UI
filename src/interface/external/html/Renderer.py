from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings
from PyQt5.QtWidgets import QSizePolicy


class Renderer(QWebEngineView):
    def __init__(self, parent, file: str):
        QWebEngineView.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.page().setWebChannel(QWebChannel(self.page()))
        with open(file, 'r', encoding="utf-8") as instructions:
            self.setHtml(instructions.read())
        self.page().webChannel().registerObject("Renderer", self)
        self.page().settings().setAttribute(QWebEngineSettings.JavascriptEnabled, True)

