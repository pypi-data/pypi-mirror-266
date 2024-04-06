from langchain_community.document_loaders import WebBaseLoader

from komodo.framework.komodo_datasource import KomodoDataSource
from komodo.shared.documents.text_extract import to_clean_text


class WebPages(KomodoDataSource):
    def __init__(self, name, pages):
        super().__init__(name, type="webpages")
        self.pages = pages

    def list_items(self):
        return self.pages

    def list_items_with_details(self):
        return self.pages

    def get_item(self, page):
        documents = WebBaseLoader(page).load()
        for d in documents:
            d.page_content = to_clean_text(d.page_content)
        return documents
