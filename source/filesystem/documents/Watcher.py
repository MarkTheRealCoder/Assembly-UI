from weakref import WeakKeyDictionary

from PyQt5.QtCore import QDateTime

from source.filesystem.documents.Document import Document


class Watcher:
    def __init__(self):
        self.___doc_map: WeakKeyDictionary[Document, QDateTime] = WeakKeyDictionary()

    def updateDocument(self, document: Document) -> None:
        self.___doc_map[document] = QDateTime.currentDateTime()

    def getDocumentUpdates(self, document: Document) -> str | None:
        text = None
        if document not in self.___doc_map:
            self.updateDocument(document)
        else:
            last_update = self.___doc_map[document]
            current_update = QDateTime.fromSecsSinceEpoch(int(document.getLastModified()))

            if last_update < current_update:
                self.___doc_map[document] = current_update
                document.reload()
                text = document.text
        return text