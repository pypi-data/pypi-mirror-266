from komodo.framework.komodo_app import KomodoApp
from komodo.loaders.database.agent_loader import AgentLoader
from komodo.loaders.database.tool_loader import ToolLoader
from komodo.store.appliance_store import ApplianceStore


class ApplianceLoader:

    @classmethod
    def load(cls, shortcode) -> KomodoApp:
        appliance = ApplianceStore().retrieve_appliance(shortcode)
        print(appliance)
        komodo_app = KomodoApp(shortcode=shortcode, name=appliance.name, purpose=appliance.purpose)

        for shortcode in appliance.agent_shortcodes:
            agent = AgentLoader.load(shortcode)
            komodo_app.add_agent(agent)

        for shortcode in appliance.tool_shortcodes:
            tool = ToolLoader.load(shortcode)
            komodo_app.add_tool(tool)

        return komodo_app


if __name__ == '__main__':
    app = ApplianceLoader.load('sample')
    print(app)
