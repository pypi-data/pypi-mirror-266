from komodo.config import PlatformConfig
from komodo.core.agents.summarizer_agent import SummarizerAgent
from komodo.core.tools.files.directory_reader import DirectoryReader
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.models.framework.agent_runner import AgentRunner


def sample_agent_runner():
    from komodo.core.tools.web.serpapi_search import SerpapiSearch

    agent = SummarizerAgent.create(100)
    print(agent.instructions)

    agent = SummarizerAgent(n=200)
    print(agent.instructions)

    runtime = KomodoRuntime(agent=agent)
    runner = AgentRunner(runtime)
    result = runner.run("Summarize the iliad in 5 words")
    print(result.text)

    agent = KomodoAgent.default()
    agent.tools = [DirectoryReader()]
    runtime = KomodoRuntime(agent=agent, config=PlatformConfig())
    runner = AgentRunner(runtime)

    prompt = "list files available to you"
    response = runner.run(prompt)
    print(response.text)

    for response in runner.run_streamed(prompt):
        print(response, end="")
    print()

    prompt = "whats up in nyc today? search for event and then search for additional details on the first event found"
    agent.tools = [SerpapiSearch()]
    for response in runner.run_streamed(prompt):
        print(response, end="")
    print()

    response = runner.run(prompt)
    print(response.text)


if __name__ == "__main__":
    sample_agent_runner()
