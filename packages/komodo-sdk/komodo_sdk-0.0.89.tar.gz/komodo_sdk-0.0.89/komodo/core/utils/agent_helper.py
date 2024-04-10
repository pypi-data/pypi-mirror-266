from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_runnable import KomodoRunnableAgent, KomodoRunner
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.loaders.filesystem.agent_loader import AgentLoader
from komodo.models.framework.agent_runner import AgentRunner


class AgentHelper:

    def __init__(self, config=None):
        self.config = config

    def load(self, shortcode, files=None, **kwargs) -> KomodoRunnableAgent:
        loader = AgentLoader(self.config.definitions_directory, self.config.data_directory)
        params = loader.load(shortcode)
        agent = KomodoRunnableAgent(AgentRunner, **{**params, **kwargs})
        if files:
            files = files if isinstance(files, list) else [files]
            for file in files:
                agent.context.add_file(file)
        return agent

    def runner(self, agent: KomodoAgent, **kwargs) -> KomodoRunner:
        runtime = KomodoRuntime(agent=agent, **kwargs)
        return AgentRunner(runtime)
