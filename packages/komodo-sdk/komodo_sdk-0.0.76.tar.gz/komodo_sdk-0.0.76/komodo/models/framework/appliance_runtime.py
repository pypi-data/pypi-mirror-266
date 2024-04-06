import copy

from werkzeug.utils import secure_filename

from komodo.core.agents.groot_agent import GrootAgent
from komodo.core.utils.rag_context import RagContext
from komodo.framework.komodo_app import KomodoApp
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.loaders.database.user_loader import UserLoader
from komodo.models.framework.agent_runner import AgentRunner
from komodo.models.framework.workflow_runner import WorkflowRunner


class ApplianceRuntime(KomodoRuntime):

    def __init__(self, appliance):
        super().__init__(appliance=appliance)
        self.appliance = appliance

    def run_agent_as_tool(self, agent, args, runtime) -> str:
        runtime = copy.copy(runtime)
        runtime.agent = agent

        runner = AgentRunner(runtime=runtime)
        history = [{'role': "system", 'content': args['system']}]
        response = runner.run(prompt=args['user'], history=history)
        return response.text

    def run_workflow_as_tool(self, workflow, args, runtime) -> str:
        runtime = copy.copy(runtime)
        runtime.workflow = workflow

        runner = WorkflowRunner(runtime=runtime)
        response = runner.run(prompt=args['command'], history=None)
        return response.text

    def get_appliance_rag_context(self):
        locations = self.appliance.config.locations()
        locations.setup_appliance(self.appliance.shortcode)
        appliance_data = locations.appliance_data(self.appliance.shortcode)
        cache_path = locations.cache_path()
        shortcode = f"appliance_{self.appliance.shortcode}"
        return RagContext(path=appliance_data, cache_path=cache_path, shortcode=shortcode)

    def get_agent_rag_context(self, agent):
        locations = self.appliance.config.locations()
        locations.setup_agent(agent.shortcode)
        agent_data = locations.agent_data(agent.shortcode)
        cache_path = locations.cache_path()
        shortcode = f"agent_{agent.shortcode}"
        return RagContext(path=agent_data, cache_path=cache_path, shortcode=shortcode)

    def get_workflow_rag_context(self, workflow):
        locations = self.appliance.config.locations()
        locations.setup_workflow(workflow.shortcode)
        workflow_data = locations.workflow_data(workflow.shortcode)
        cache_path = locations.cache_path()
        shortcode = f"workflow_{workflow.shortcode}"
        return RagContext(path=workflow_data, cache_path=cache_path, shortcode=shortcode)

    def get_collection_rag_context(self, user, collection):
        locations = self.appliance.config.locations()
        locations.setup_user(user.email)
        collection_data = locations.user_collections(user.email) / secure_filename(collection.path)
        cache_path = locations.cache_path()
        shortcode = collection.shortcode
        return RagContext(path=collection_data, cache_path=cache_path, shortcode=shortcode)

    def get_user(self, email):
        user = UserLoader.load(email) or next((x for x in self.appliance.users if x.email == email), None)
        if UserLoader.is_power_user(email):
            user.show_tool_progress = "details"
        return user

    def get_all_agents(self):
        return self.appliance.get_all_agents()

    def get_agent(self, shortcode):
        for a in self.get_all_agents():
            if a.shortcode == shortcode:
                return a
        return None

    def get_capabilities_of_agents(self):
        t = [
            "{}. {} ({}): {}".format(i, a.name, a.shortcode, a.purpose)
            for i, a in enumerate(self.get_all_agents(), start=1)
            if a.purpose is not None
        ]
        return '\n'.join(t)

    def get_capabilities_of_tools(self):
        t = ["{}. {}: {}".format(i + 1, tool.shortcode, tool.purpose)
             for i, tool in enumerate(filter(lambda x: x.purpose is not None, self.appliance.tools))]
        return '\n'.join(t)

    def list_capabilities(self):
        return "I am " + self.appliance.name + \
            " appliance and my purpose is " + self.appliance.purpose + "." + \
            "\n\nI have agents with these capabilities: \n" + self.get_capabilities_of_agents() + \
            "\n\nI have tools with these capabilities: \n" + self.get_capabilities_of_tools()


if __name__ == '__main__':
    appliance = KomodoApp.default()
    appliance.add_agent(GrootAgent())
    runtime = ApplianceRuntime(appliance)
    print(runtime.list_capabilities())
