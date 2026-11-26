import threading
import webbrowser

from PyQt5.QtCore import QUrl, pyqtSignal
from PyQt5.QtWebChannel import QWebChannel
from PyQt5.QtWebEngineWidgets import QWebEngineView, QWebEngineSettings, QWebEnginePage, QWebEngineProfile
from PyQt5.QtWidgets import QSizePolicy


class CustomWebEnginePage(QWebEnginePage):
    """Page that opens clicked web links in the system browser and has no context menu."""
    ___EXTERNAL_SCHEMES = ("http", "https", "mailto")

    def __init__(self, parent=None):
        super().__init__(parent)

    def acceptNavigationRequest(self, url: QUrl, nav_type: QWebEnginePage.NavigationType, is_main_frame):
        if nav_type == QWebEnginePage.NavigationTypeLinkClicked and url.scheme() in self.___EXTERNAL_SCHEMES:
            webbrowser.open(url.toString())
            return False  # Prevent the web engine from navigating to the URL
        return True

    def createStandardContextMenu(self):
        return None


class Renderer(QWebEngineView):
    """
    Web view that renders an HTML file with JavaScript enabled.
    A background thread reads the file, so the GUI thread only creates the view.
    """
    contentLoaded = pyqtSignal(str)

    def __init__(self, parent, file: str):
        QWebEngineView.__init__(self, parent)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        custom_page = CustomWebEnginePage(self)
        self.setPage(custom_page)

        self.page().setWebChannel(QWebChannel(self.page()))
        self.page().webChannel().registerObject("Renderer", self)
        settings = self.page().settings()
        settings.setAttribute(QWebEngineSettings.JavascriptEnabled, True)
        settings.setAttribute(QWebEngineSettings.JavascriptCanAccessClipboard, True)
        settings.setAttribute(QWebEngineSettings.LocalContentCanAccessFileUrls, True)

        self.___file = file
        self.contentLoaded.connect(self.___showContent)
        threading.Thread(target=self.___readContent, name="HelpReader", daemon=True).start()

    def ___readContent(self):
        try:
            with open(self.___file, "r", encoding="utf-8") as page:
                content = page.read()
        except OSError as error:
            content = f"<body style='background:#1E1E1E;color:#CCCCCC'>Cannot open {self.___file}: {error}</body>"
        try:
            self.contentLoaded.emit(content)
        except RuntimeError:
            pass  # The window closed before the file was read.

    def ___showContent(self, content: str):
        # The base URL lets the page load its stylesheet and fonts from the resources folder.
        self.setHtml(content, QUrl.fromLocalFile(self.___file))


_WARM_PAGE = None


def warmUpWebEngine():
    """
    Start the web engine before the first help page opens.
    The first page of the process starts the web engine on the GUI thread, which blocks the application for a moment.
    The page is deleted after it loads, so it does not outlive the web engine profile when the application exits.
    """
    global _WARM_PAGE
    if _WARM_PAGE is not None:
        return
    _WARM_PAGE = QWebEnginePage(QWebEngineProfile.defaultProfile())
    _WARM_PAGE.loadFinished.connect(_WARM_PAGE.deleteLater)
    _WARM_PAGE.setHtml("")
