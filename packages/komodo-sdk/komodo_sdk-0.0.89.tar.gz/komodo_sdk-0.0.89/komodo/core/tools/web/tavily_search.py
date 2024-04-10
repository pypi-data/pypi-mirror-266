import os
import time

from requests import HTTPError
from tavily import TavilyClient

from komodo.framework.komodo_tool import KomodoTool
from komodo.shared.utils.sentry_utils import sentry_trace
from komodo.shared.utils.term_colors import print_warning


class TavilySearch(KomodoTool):
    name = "Tavily Web Search"
    purpose = "Accesses real-time data and insights from a wide range of internet sources, tailored to specific queries. Ideal for gathering current information on various topics."
    shortcode = "komodo_tavily_search"

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
                        "description": "Specify the search query to retrieve up-to-date and relevant information. Suitable for a broad spectrum of topics, ensuring accurate and professionally curated content."
                    },
                },
                "required": ["query"]
            }
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)
        self.api_key = self.get_tavily_api_key()
        if not self.api_key:
            print_warning("No Tavily key found. Please set the environment variable TAVILY_API_KEY")

    def get_tavily_api_key(self):
        return os.getenv("TAVILY_API_KEY", "")

    # Function to perform a Tavily search
    @sentry_trace
    def action(self, args):
        attempts = 0
        while attempts < 3:
            try:
                tavily_client = TavilyClient(self.api_key)
                search_result = tavily_client.get_search_context(args["query"], search_depth="advanced",
                                                                 max_tokens=8000)
                return search_result
            except HTTPError as e:
                if e.response.status_code == 429 or e.response.status_code == 502:
                    print("Attempt# " + str(attempts) + " Error: " + str(e))
                    print("Rate limit exceeded. Waiting for 5 seconds...")
                    time.sleep(5)
                    attempts += 1
        return "Failed to retrieve search results"


if __name__ == "__main__":
    tool = TavilySearch()
    print(tool.definition)
    print(tool.action({"query": "Nvidia stock"}))
