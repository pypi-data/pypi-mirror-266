import copy

from komodo.core.agents.groot_agent import GrootAgent
from komodo.framework.komodo_app import KomodoApp
from komodo.models.framework.agent_runner import AgentRunner
from komodo.models.framework.workflow_runner import WorkflowRunner


class ApplianceUtils:
    def __init__(self, appliance):
        self.appliance = appliance

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


if __name__ == '__main__':
    appliance = KomodoApp.default()
    appliance.add_agent(GrootAgent())
    utils = ApplianceUtils(appliance)
    print(utils.list_capabilities())
