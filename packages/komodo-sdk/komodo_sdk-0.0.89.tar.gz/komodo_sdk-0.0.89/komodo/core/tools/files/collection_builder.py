import os
from pathlib import Path

import magic
import requests
from serpapi.core import search
from werkzeug.utils import secure_filename

from komodo.config import PlatformConfig
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool import KomodoTool
from komodo.framework.komodo_user import KomodoUser
from komodo.proto.generated.collection_pb2 import Collection, QnA
from komodo.shared.utils.digest import get_text_digest
from komodo.shared.utils.filestats import file_details
from komodo.shared.utils.sentry_utils import sentry_trace
from komodo.store.collection_store import CollectionStore
from komodo.store.proto_utils import convert_proto_to_dict


class CollectionBuilder(KomodoTool):
    name = "Collection Builder Tool"
    purpose = "Given a query, searches the web for matching PDFs and retrieves them into a collection for use."
    shortcode = "collection_builder"

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
                    "name": {
                        "type": "string",
                        "description": "Name of the folder to created. Short name for the collection."
                    },
                    "start": {
                        "type": "integer",
                        "description": "Parameter defines the result offset. It skips the given number of results. It's used for pagination. Default is 0."
                    },
                    "num": {
                        "type": "integer",
                        "description": "Parameter defines the maximum number of results to return. Default is 10."
                    },
                    "sites": {
                        "type": "string",
                        "description": "Parameter defines the site to search. It can be a single website or a list of websites separated by commas."
                    },
                    "filetype": {
                        "type": "string",
                        "description": "Filetype to filter the search results. Default is 'pdf'."
                    },
                    "tbm": {
                        "type": "string",
                        "description": """(to be matched) parameter defines the type of search you want to do.
                            It can be set to:
                            (no tbm parameter): regular Google Search,
                            isch: Google Images API,
                            lcl - Google Local API
                            vid: Google Videos API,
                            nws: Google News API,
                            shop: Google Shopping API,
                            pts: Google Patents API,
                            or any other Google service.
                        """
                    },
                },
                "required": ["query", "name"]
            }
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)

    @sentry_trace
    def action(self, args, runtime: KomodoRuntime):
        api_key = runtime.config.get_secret('SERP_API_KEY')
        base_path = runtime.config.locations().user_collections(runtime.user.email)

        q = args.pop("query")
        n = args.pop("name")

        # Search the web using Google search and filter PDF results
        response = self.search(q, api_key=api_key, **args)
        if not response or not response.data or not response.data.get('organic_results'):
            return "No results found."

        results = response.data['organic_results']
        urls = [result['link'] for result in results]

        # Create a new collection
        shortcode = get_text_digest(q + str(urls))
        name = n or shortcode
        folder = Path(base_path) / name
        os.makedirs(folder, exist_ok=True)

        collection = Collection()
        collection.name = "Auto Researcher: " + q
        collection.path = str(folder)
        collection.shortcode = shortcode
        collection.description = "Collection of PDFs retrieved from the web given query: " + q
        collection.query = q

        if 'related_questions' in response.data:
            for question in response.data['related_questions']:
                qna = QnA()
                qna.question = question.get('question', '')
                qna.answer = question.get('snippet', '')
                qna.snippet = question.get('snippet', '')
                qna.source = question.get('source', '')
                qna.title = question.get('title', '')
                collection.questions.append(qna)

        # Process the retrieved PDF URLs
        for result in response.data['organic_results']:
            url = result['link']
            try:
                # Download the PDF file
                pdf_content = self.download_pdf(url)
                if "PDF" not in magic.from_buffer(pdf_content):
                    print(f"File at {url} is not a PDF")
                    continue

                pdf_name = secure_filename(result.get('title', q[:32])) + ".pdf"
                filepath = folder / pdf_name
                self.save_pdf(pdf_content, filepath)

                file = file_details(filepath)
                file.description = f"PDF file retrieved from {url}"
                file.search_result.url = result.get('link', '')
                file.search_result.title = result.get('title', '')
                file.search_result.snippet = result.get('snippet', '')
                file.search_result.source = result.get('source', '')

                collection.files.append(file)

            except Exception as e:
                print(f"Failed to process PDF from {url}: {e}")

        if len(collection.files) > 0:
            store = CollectionStore()
            store.store_collection(collection)
            store.add_user_collection(runtime.user.email, collection.shortcode)
            print(f"Collection created with {len(collection.files)} files: {collection.shortcode}")

        return f"Collection: {collection.shortcode} created with {len(collection.files)} files: " + str(
            convert_proto_to_dict(collection))

    def search(self, query, *, api_key, **kwargs):
        """
        Search the web using Google search and filter PDF results.
        """
        filetype = kwargs.pop("filetype", "pdf")
        filetype_filter = f"filetype:{filetype} "

        sites = kwargs.pop("sites", "").split(",")
        site_filter = "".join([f"site:{site} " for site in sites if site])

        composite_query = filetype_filter + site_filter + query
        print(f"Searching for: {composite_query}")
        try:
            # Perform Google search with the query and filter PDF results
            response = search(q=composite_query, api_key=api_key, **kwargs)
            return response
        except Exception as e:
            print(f"Failed to search {query} for filetype: {filetype}: {e}")
            return []

    def download_pdf(self, url):
        """
        Download the PDF file from the given URL.
        """
        try:
            response = requests.get(url)
            return response.content
        except Exception as e:
            print(f"Failed to download PDF from {url}: {e}")
            return None

    def save_pdf(self, pdf_content, filepath):
        """
        Save the PDF content to the collection folder.
        """
        if pdf_content:
            with open(filepath, "wb") as pdf:
                pdf.write(pdf_content)
        else:
            print("Failed to save PDF content to file: " + str(filepath))


if __name__ == "__main__":
    config = PlatformConfig()
    user = KomodoUser.default()
    runtime = KomodoRuntime(config=config, user=user)
    tool = CollectionBuilder()
    print(tool.definition)
    # print(tool.action({"query": "Latest on Nvidia stock"}, runtime))
    # print(tool.action({"query": "patents on swimming products", "num": 5, "filetype": "pdf", "tbm": "pts"}, runtime))
    print(tool.action({"query": "consulting services site:gartner.com", "name": "foo-fa", "num": 5}, runtime))
