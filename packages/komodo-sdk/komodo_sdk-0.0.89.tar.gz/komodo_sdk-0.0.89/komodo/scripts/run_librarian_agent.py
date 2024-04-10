from komodo.core.agents.librarian_agent import LibrarianAgent
from komodo.core.utils.rag_context import RagContext
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.models.framework.agent_runner import AgentRunner


def run_search():
    from komodo.config import PlatformConfig
    config = PlatformConfig()
    agent = LibrarianAgent(RagContext(path=config.komodo_path, cache_path=config.cache()))
    agent.index()

    runtime = KomodoRuntime(agent=agent)
    runner = AgentRunner(runtime)

    response = runner.run("What did the G20 leaders agreed in 2009?")
    print(response.text)

    response = runner.run("tell me more about unique swap identifiers (USI) of each clearing swap?")
    print(response.text)


if __name__ == "__main__":
    run_search()
