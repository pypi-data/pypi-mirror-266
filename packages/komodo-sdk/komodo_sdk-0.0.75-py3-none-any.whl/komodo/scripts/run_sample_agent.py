from komodo.config import PlatformConfig
from komodo.core.agents.sample_agent import SampleAgent
from komodo.models.framework.agent_runner import AgentRunner

if __name__ == "__main__":
    path = PlatformConfig().komodo_hello_path
    agent = SampleAgent(path)
    runner = AgentRunner(agent)
    response = runner.run("Call the sample tool with hello.txt file and call hello_world function.")
    print(response.text)
