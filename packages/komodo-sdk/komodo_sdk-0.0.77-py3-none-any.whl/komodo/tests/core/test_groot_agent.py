from komodo.core.agents.groot_agent import GrootAgent
from komodo.models.framework.agent_runner import AgentRunner


def test_groot():
    groot_agent = GrootAgent()
    print(groot_agent.to_dict())
    print(groot_agent.generate_context())

    runner = AgentRunner(groot_agent)
    prompt = "What is the purpose of groot?"
    response = runner.run(prompt)
    print(response.text)
