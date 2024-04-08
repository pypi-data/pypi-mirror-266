from komodo.framework.komodo_runnable import KomodoRunner
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.models.framework.model_request import ModelRequest
from komodo.models.framework.responder import get_model_response
from komodo.models.openai.openai_api_streamed import openai_chat_response_streamed


class AgentRunner(KomodoRunner):
    def __init__(self, runtime: KomodoRuntime):
        super().__init__(runtime=runtime)

    def run(self, prompt, **kwargs) -> str:
        request = ModelRequest(prompt=prompt, runtime=self.runtime, **kwargs)
        response = get_model_response(request)
        return response.text

    def run_streamed(self, prompt, **kwargs):
        request = ModelRequest(prompt=prompt, runtime=self.runtime, **kwargs)
        for response in openai_chat_response_streamed(request):
            yield response

    def run_debug(self, prompt, **kwargs):
        request = ModelRequest(prompt=prompt, runtime=self.runtime, **kwargs)
        response = get_model_response(request)
        return response
