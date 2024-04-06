from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_user import KomodoUser
from komodo.models.framework.agent_runner import AgentRunner

if __name__ == '__main__':
    from komodo.core.tools.utils.thought_tool import ChainOfThought
    from komodo.models.framework.models import OPENAI_GPT4_MODEL

    agent = KomodoAgent.default()
    agent.model = OPENAI_GPT4_MODEL
    agent.add_tool(ChainOfThought())
    runner = AgentRunner(agent, user=KomodoUser.poweruser())
    
    prompt = "Tell me 5 jokes, and invoke the thought tool exactly after telling each joke."
    for response in runner.run_streamed(prompt):
        print(response, end="")
    print()
