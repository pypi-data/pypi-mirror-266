from datetime import datetime

from komodo.models.framework.model_request import ModelRequest
from komodo.models.framework.model_response import ModelResponse
from komodo.models.openai.openai_api import openai_chat_response


def get_model_response(request: ModelRequest) -> ModelResponse:
    start_time = datetime.now()
    agent = request.runtime.agent
    if agent.provider is not None:
        if agent.provider == "openai":
            response = openai_chat_response(request)
        else:
            raise Exception("Unknown provider: " + agent.provider)
    else:
        raise Exception("No provider specified for assistant: " + agent.shortcode)

    response.started = start_time.timestamp()
    response.completed = datetime.now().timestamp()
    return response
