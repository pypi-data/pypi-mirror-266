from komodo.models.framework.model_response import ModelResponse


class Runner:

    def run(self, prompt, **kwargs) -> ModelResponse:
        raise NotImplementedError

    def run_streamed(self, prompt, **kwargs):
        raise NotImplementedError
