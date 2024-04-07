from bs4 import BeautifulSoup as Soup
from langchain_community.document_loaders.recursive_url_loader import RecursiveUrlLoader

from komodo.framework.komodo_datasource import KomodoDataSource
from komodo.shared.documents.text_extract import to_clean_text


class WebsiteCrawler(KomodoDataSource):

    def __init__(self, name, site, depth=2):
        super().__init__(name, type="website_crawler")
        self.site = site
        self.depth = depth

    def list_items(self):
        return [self.site]

    def list_items_with_details(self):
        return [self.site]

    def get_item(self, key):
        extractor = lambda x: Soup(x, "html.parser").text
        documents = RecursiveUrlLoader(url=self.site, max_depth=self.depth, extractor=extractor).load()
        for d in documents:
            d.page_content = to_clean_text(d.page_content)
        return documents
