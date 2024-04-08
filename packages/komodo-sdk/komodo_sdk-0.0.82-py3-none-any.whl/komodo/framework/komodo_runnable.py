from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_runtime import KomodoRuntime


class KomodoRunner:

    def __init__(self, runtime=None):
        self.runtime = runtime or KomodoRuntime()

    def run(self, prompt, **kwargs):
        raise NotImplementedError

    def run_streamed(self, prompt, **kwargs):
        raise NotImplementedError


class KomodoRunnableAgent(KomodoAgent):
    def __init__(self, agent_runner, **kwargs):
        super().__init__(**kwargs)
        if agent_runner:
            self.runner = agent_runner(KomodoRuntime(agent=self)) if callable(agent_runner) else agent_runner

    def get_prompt(self, prompt=None):
        prompt = prompt or self.kwargs.get('prompt')
        if prompt is None:
            raise Exception("Prompt is required for agent to run.")
        return prompt

    def run(self, prompt=None, **kwargs):
        if not self.runner:
            raise Exception("Agent runner is not defined.")
        return self.runner.run(self.get_prompt(prompt), **kwargs)

    def run_streamed(self, prompt, **kwargs):
        if not self.runner:
            raise Exception("Agent runner is not defined.")
        for response in self.runner.run_streamed(self.get_prompt(prompt), **kwargs):
            yield response
