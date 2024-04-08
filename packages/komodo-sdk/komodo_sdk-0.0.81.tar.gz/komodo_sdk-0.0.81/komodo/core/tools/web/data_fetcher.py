import requests
from serpapi.core import search

from komodo.config import PlatformConfig
from komodo.framework.komodo_tool import KomodoTool
from komodo.shared.utils.sentry_utils import sentry_trace


class DataFetcher(KomodoTool):
    name = "Data Fetcher Tool"
    purpose = "Given a query, searches the web for matching PDFs and retrieves them into the path provided."
    shortcode = "komodo_data_fetcher"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Enter your search terms for detailed results, such as 'Latest on Nvidia stock'. Ensures safe, accurate, and professional searches."
                    },
                },
                "required": ["query"]
            }
        }
    }

    def __init__(self, api_key):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)
        self.api_key = api_key

    @sentry_trace
    def action(self, args):
        attempts = 0
        q = args["query"] if "query" in args else args["q"]
        params_dict = {"q": q, "api_key": self.api_key}

        # Search the web using Google search and filter PDF results
        pdf_urls = self.search_pdf_urls(q)

        # Process the retrieved PDF URLs
        for url in pdf_urls:
            # Download the PDF file
            pdf_content = self.download_pdf(url)
            # Process the PDF content as needed

    def search_pdf_urls(self, query):
        """
        Search the web using Google search and filter PDF results.
        """
        pdf_urls = []
        try:
            # Perform Google search with the query and filter PDF results
            search_results = search(q=query + " filetype:pdf", api_key=self.api_key, num=10, stop=10, pause=2)
            pdf_urls = [item['link'] for item in search_results.data['organic_results']]
        except Exception as e:
            print("Error occurred while searching:", e)
        return pdf_urls

    def download_pdf(self, url):
        """
        Download the PDF file from the given URL.
        """
        try:
            response = requests.get(url)
            if response.status_code == 200:
                # Return the PDF content
                return response.content
            else:
                print("Error downloading PDF:", response.text)
        except Exception as e:
            print("Error occurred while downloading PDF:", e)
        return None


if __name__ == "__main__":
    config = PlatformConfig()
    tool = DataFetcher(config.get_serpapi_key())
    print(tool.definition)
    print(tool.action({"query": "Latest on Nvidia stock"}))
