from komodo.core.agents.groot_agent import GrootAgent
from komodo.core.tools.files.directory_reader import DirectoryReader
from komodo.core.tools.files.file_reader import FileReader
from komodo.core.tools.files.file_writer import FileWriter
from komodo.core.tools.utils.agent_tool import AgentAsTool
from komodo.core.tools.utils.workflow_tool import WorkflowAsTool
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_app import KomodoApp
from komodo.framework.komodo_tool import KomodoTool
from komodo.models.framework.models import OPENAI_GPT4_MODEL


class CoordinatorAgent(KomodoAgent):
    model = OPENAI_GPT4_MODEL
    instructions = '''
    Act like an authoritative orchestrator of tasks. 
    You are responsible for managing workflow using tools provided.
            
    Take time to understand the context and the goal of the task, break down the 
    tasks and order in which to call the other agents. 
    Create prompts for each tool based on task requirements and inputs.
            
    You MAY have to wait for response from one agent to feed into the other agents.
    
    The conversation history has tool outputs of the agents. 
    You must manage the conversation by providing the right prompts and inputs to the agents. 
    Make appropriate assumptions when talking to these agents, and provide them the right context.
    
    User file_reader to read files, and file_writer to write files.
    '''

    def __init__(self, appliance: KomodoApp, run_agent_as_tool, run_workflow_as_tool):
        super().__init__(shortcode=appliance.shortcode + "_coordinator",
                         name=appliance.name + " Coordinator Agent",
                         purpose=appliance.purpose,
                         model=self.model,
                         instructions=self.instructions)

        self.appliance = appliance

        self.add_tool(DirectoryReader())
        self.add_tool(FileReader())
        self.add_tool(FileWriter())

        for agent in appliance.agents:
            self.add_tool(AgentAsTool(agent, run_agent_as_tool))

        for tool in appliance.tools:
            self.add_tool(tool)

        for workflow in appliance.workflows:
            self.add_tool(WorkflowAsTool(workflow, run_workflow_as_tool))

    def generate_context(self, prompt=None, runtime=None):
        return self.appliance.generate_context(prompt=prompt)


if __name__ == '__main__':
    from komodo.config import PlatformConfig

    appliance = KomodoApp.default(config=PlatformConfig())
    appliance.add_agent(GrootAgent())
    agent = CoordinatorAgent(appliance, lambda agent: KomodoTool.default(), lambda workflow: KomodoTool.default())
    print(agent)
    print(agent.to_dict())
    print(agent.generate_context())
