from komodo.framework.komodo_runnable import KomodoRunner
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.models.framework.model_request import ModelRequest
from komodo.models.framework.model_response import ModelResponse
from komodo.models.framework.responder import get_model_response
from komodo.models.openai.openai_api_streamed import openai_chat_response_streamed
from komodo.shared.utils.term_colors import print_gray


class AgentRunner(KomodoRunner):
    def __init__(self, runtime: KomodoRuntime):
        super().__init__(runtime=runtime)

    def run(self, prompt, **kwargs) -> ModelResponse:
        request = ModelRequest(prompt=prompt, runtime=self.runtime, **kwargs)
        print_gray("Requesting response for: ", request)
        response = get_model_response(request)
        return response

    def run_streamed(self, prompt, **kwargs):
        request = ModelRequest(prompt=prompt, runtime=self.runtime, **kwargs)
        print_gray("Requesting streamed response for: ", request)
        for response in openai_chat_response_streamed(request):
            yield response
