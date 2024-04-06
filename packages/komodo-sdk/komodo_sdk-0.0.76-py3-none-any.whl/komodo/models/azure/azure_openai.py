from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_user import KomodoUser
from komodo.models.azure.azure import get_azure_openai_client
from komodo.models.framework.model_request import ModelRequest
from komodo.models.framework.model_response import ModelResponse
from komodo.models.framework.models import AZURE_OPENAI_GPT35_MODEL
from komodo.models.openai.openai_api import openai_chat_response_with_client
from komodo.shared.utils.sentry_utils import sentry_trace


@sentry_trace
def azure_assistant_response(request: ModelRequest) -> ModelResponse:
    client = get_azure_openai_client(request.agent.model)
    return openai_chat_response_with_client(client, request)


# model ids are deployment names at Azure OpenAI
@sentry_trace
def azure_openai_invoke(prompt, model=AZURE_OPENAI_GPT35_MODEL) -> ModelResponse:
    client = get_azure_openai_client(model)
    request = ModelRequest(prompt=prompt, user=KomodoUser.default(), agent=KomodoAgent.default())
    return openai_chat_response_with_client(client, request)
