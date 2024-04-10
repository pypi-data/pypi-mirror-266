from komodo.core.tools.utils.sample_tool import SampleTool
from komodo.core.tools.utils.thought_tool import ChainOfThought
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_user import KomodoUser
from komodo.models.framework.agent_runner import AgentRunner


def run_stream_1():
    prompt = "whats up in nyc today? search for event and then search for additional details on the first event found"
    agent = KomodoAgent.default()
    agent.tools = [SampleTool("."), ChainOfThought()]
    runner = AgentRunner(agent, user=KomodoUser.poweruser())
    for response in runner.run_streamed(prompt):
        print(response, end="")
    print()


if __name__ == "__main__":
    run_stream_1()
