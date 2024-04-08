import json
import time

from requests import HTTPError
from serpapi import GoogleSearch

from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool import KomodoTool
from komodo.shared.utils.sentry_utils import sentry_trace


class SerpapiSearch(KomodoTool):
    name = "Web Search Tool"
    purpose = "Leverages SerpApi to conduct detailed web searches across various search engines. It supports a wide range of parameters as documented in SerpApi's guidelines."
    shortcode = "komodo_serpapi_search"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "engine": {
                        "type": "string",
                        "description": "Select the search engine (must be one of: google, bing, baidu, google_scholar, yandex, ebay, yahoo, home_depot, youtube). Default is google."
                    },
                    "query": {
                        "type": "string",
                        "description": "Enter your search terms for detailed results, such as 'Latest on Nvidia stock'. Ensures safe, accurate, and professional searches."
                    },
                    "location": {
                        "type": "string",
                        "description": "Optional location setting for localized search results, like 'New York, New York'."
                    },
                    "params": {
                        "type": "object",
                        "description": "Additional parameters for customizing the search, in line with SerpApi's options (e.g., {'hl': 'en'})."
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

    @sentry_trace
    def action(self, args, runtime: KomodoRuntime):
        attempts = 0
        api_key = runtime.config.get_secret('SERP_API_KEY')
        q = args["query"] if "query" in args else args["q"]
        params_dict = {"q": q, "api_key": api_key}

        if "engine" in args:
            params_dict["engine"] = args["engine"]

        if "location" in args:
            params_dict["location"] = args["location"]

        if "params" in args:
            params_dict.update(args["params"])

        while attempts < 3:
            try:
                search = GoogleSearch(params_dict)
                result = self.process_response(search.get_dict())
                return json.dumps(result, default=vars)
                # Convert to JSON,
                # TBD: should only return result['search_information'] and result['organic_results']
                # to be consistent with Tavily and improve performance

            except HTTPError as e:
                if e.response.status_code == 429 or e.response.status_code == 502:
                    print("Attempt# " + str(attempts) + " Error: " + str(e))
                    print("Rate limit exceeded. Waiting for 5 seconds...")
                    time.sleep(5)
                    attempts += 1

            except Exception as e:
                print("Error: " + str(e))
                return "Could not complete the web search. Encountered error: " + str(e)

        return "Could not successfully search after multiple attempts: " + q

    @staticmethod
    def process_response(res: dict) -> str:
        """Process response from SerpAPI."""
        if "error" in res.keys():
            raise ValueError(f"Got error from SerpAPI: {res['error']}")
        if "answer_box_list" in res.keys():
            res["answer_box"] = res["answer_box_list"]
        if "answer_box" in res.keys():
            answer_box = res["answer_box"]
            if isinstance(answer_box, list):
                answer_box = answer_box[0]
            if "result" in answer_box.keys():
                return answer_box["result"]
            elif "answer" in answer_box.keys():
                return answer_box["answer"]
            elif "snippet" in answer_box.keys():
                return answer_box["snippet"]
            elif "snippet_highlighted_words" in answer_box.keys():
                return answer_box["snippet_highlighted_words"]
            else:
                answer = {}
                for key, value in answer_box.items():
                    if not isinstance(value, (list, dict)) and not (
                            isinstance(value, str) and value.startswith("http")
                    ):
                        answer[key] = value
                return str(answer)
        elif "events_results" in res.keys():
            return res["events_results"][:10]
        elif "sports_results" in res.keys():
            return res["sports_results"]
        elif "top_stories" in res.keys():
            return res["top_stories"]
        elif "news_results" in res.keys():
            return res["news_results"]
        elif "jobs_results" in res.keys() and "jobs" in res["jobs_results"].keys():
            return res["jobs_results"]["jobs"]
        elif (
                "shopping_results" in res.keys()
                and "title" in res["shopping_results"][0].keys()
        ):
            return res["shopping_results"][:3]
        elif "questions_and_answers" in res.keys():
            return res["questions_and_answers"]
        elif (
                "popular_destinations" in res.keys()
                and "destinations" in res["popular_destinations"].keys()
        ):
            return res["popular_destinations"]["destinations"]
        elif "top_sights" in res.keys() and "sights" in res["top_sights"].keys():
            return res["top_sights"]["sights"]
        elif (
                "images_results" in res.keys()
                and "thumbnail" in res["images_results"][0].keys()
        ):
            return str([item["thumbnail"] for item in res["images_results"][:10]])

        snippets = []
        if "knowledge_graph" in res.keys():
            knowledge_graph = res["knowledge_graph"]
            title = knowledge_graph["title"] if "title" in knowledge_graph else ""
            if "description" in knowledge_graph.keys():
                snippets.append(knowledge_graph["description"])
            for key, value in knowledge_graph.items():
                if (
                        isinstance(key, str)
                        and isinstance(value, str)
                        and key not in ["title", "description"]
                        and not key.endswith("_stick")
                        and not key.endswith("_link")
                        and not value.startswith("http")
                ):
                    snippets.append(f"{title} {key}: {value}.")

        for organic_result in res.get("organic_results", []):
            if "snippet" in organic_result.keys():
                snippets.append(organic_result["snippet"])
            elif "snippet_highlighted_words" in organic_result.keys():
                snippets.append(organic_result["snippet_highlighted_words"])
            elif "rich_snippet" in organic_result.keys():
                snippets.append(organic_result["rich_snippet"])
            elif "rich_snippet_table" in organic_result.keys():
                snippets.append(organic_result["rich_snippet_table"])
            elif "link" in organic_result.keys():
                snippets.append(organic_result["link"])

        if "buying_guide" in res.keys():
            snippets.append(res["buying_guide"])
        if "local_results" in res.keys() and "places" in res["local_results"].keys():
            snippets.append(res["local_results"]["places"])

        if len(snippets) > 0:
            return str(snippets)
        else:
            return "No good search result found"
