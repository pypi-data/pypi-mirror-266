from komodo.framework.komodo_agent import KomodoAgent
from komodo.loaders.database.tool_loader import ToolLoader
from komodo.store.agent_store import AgentStore


class AgentLoader:
    @classmethod
    def load(cls, shortcode) -> KomodoAgent:
        agent = AgentStore().retrieve_agent(shortcode)
        komodo_agent = KomodoAgent(name=agent.name,
                                   instructions=agent.instructions,
                                   purpose=agent.purpose,
                                   model=agent.model,
                                   provider=agent.provider,
                                   shortcode=agent.shortcode,
                                   email=agent.email,
                                   output_format=agent.output_format)

        for shortcode in agent.tool_shortcodes:
            tool = ToolLoader.load(shortcode)
            komodo_agent.add_tool(tool)

        return komodo_agent
