from komodo.core.agents.difference_agent import DifferenceAgent
from komodo.core.utils.rag_context import RagContext
from komodo.models.framework.agent_runner import AgentRunner


def run_difference():
    from komodo.config import PlatformConfig
    path = PlatformConfig().locations().appliance_data('komodo') / "diff"
    cache_path = PlatformConfig().cache()

    agent = DifferenceAgent(shortcode="difference_agent",
                            rc1=RagContext(path=path / "test1", cache_path=cache_path),
                            rc2=RagContext(path=path / "test2", cache_path=cache_path))
    agent.index()
    runner = AgentRunner(agent)
    response = runner.run("tell me more about unique swap identifiers (USI) of each clearing swap?")
    print(response.text)


if __name__ == "__main__":
    run_difference()
