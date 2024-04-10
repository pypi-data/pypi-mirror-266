import os

from komodo.models.framework.models import AZURE_OPENAI_GPT4_MODEL
from komodo.shared.utils.lambda_utils import lambda_fetch_secret


def get_azure_openai_client(model):
    from openai import AzureOpenAI

    if model == AZURE_OPENAI_GPT4_MODEL:
        return AzureOpenAI(
            api_key=get_azure_secret("AZURE_OPENAI_EASTUS2_KEY"),
            api_version=get_azure_secret("AZURE_OPENAI_EASTUS2_VERSION"),
            azure_endpoint=get_azure_secret("AZURE_OPENAI_EASTUS2_ENDPOINT")
        )

    client = AzureOpenAI(
        api_key=get_azure_secret("AZURE_OPENAI_KEY"),
        api_version=get_azure_secret("AZURE_OPENAI_VERSION"),
        azure_endpoint=get_azure_secret("AZURE_OPENAI_ENDPOINT")
    )

    return client


def get_azure_secret(name):
    return os.environ[name] if name in os.environ else lambda_fetch_secret(name)
