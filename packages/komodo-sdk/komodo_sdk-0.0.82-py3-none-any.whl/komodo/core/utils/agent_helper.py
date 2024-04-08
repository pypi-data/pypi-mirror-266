from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_runnable import KomodoRunnableAgent, KomodoRunner
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.loaders.filesystem.agent_loader import AgentLoader
from komodo.models.framework.agent_runner import AgentRunner


class AgentHelper:

    def __init__(self):
        pass

    def build_runnable_agent(self, shortcode, config, **kwargs) -> KomodoRunnableAgent:
        loader = AgentLoader(config.definitions_directory, config.data_directory)
        agent = loader.load(shortcode)
        return KomodoRunnableAgent(AgentRunner, **{**agent, **kwargs})

    def get_runner(self, agent: KomodoAgent, **kwargs) -> KomodoRunner:
        runtime = KomodoRuntime(agent=agent, **kwargs)
        return AgentRunner(runtime)
