import os

from serpapi import GoogleSearch

from komodo.config import PlatformConfig
from komodo.core.tools.web.serpapi_search import SerpapiSearch


def create_target():
    api_key = PlatformConfig().get_serpapi_key()
    return SerpapiSearch(api_key)


def test_serpapi_google():
    search = GoogleSearch({
        "q": "kineo capital",
        "location": "New York, New York",
        "api_key": os.environ["SERP_API_KEY"]
    })
    result = search.get_dict()
    print(f'result:{result}')
    return result


def test_serpapi_bing():
    search = GoogleSearch({
        "engine": "bing",
        "q": "kineo capital",
        "location": "New York, New York",
        "api_key": os.environ["SERP_API_KEY"]
    })
    result = search.get_dict()
    print(f'result:{result}')
    return result


def test_serpapi_search():
    search = create_target()
    print(search.definition)
    print(search.action({"query": "Nvidia news"}))


def test_serpapi_search_action():
    search = create_target()
    print(search.action({"query": "Kineo Capital"}))


def test_serpapi_search_action_bing():
    search = create_target()
    print(search.action({"query": "Kineo Capital", "engine": "bing"}))


def test_serpapi_search_action_params():
    search = create_target()
    print(search.action({"query": "Kineo Capital", "engine": "bing", "params": {"hl": "fr"}}))
