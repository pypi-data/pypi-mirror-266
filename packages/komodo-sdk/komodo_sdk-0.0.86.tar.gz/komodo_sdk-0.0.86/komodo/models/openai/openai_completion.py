import os

from openai import OpenAI


def fetch_openai_api_key():
    return os.getenv("OPENAI_API_KEY", "")


def openai_client():
    api_key = os.getenv("OPENAI_API_KEY", None)
    if not api_key:
        api_key = fetch_openai_api_key()
        os.environ["OPENAI_API_KEY"] = api_key

    client = OpenAI(api_key=api_key)
    return client
