from komodo.core.agents.sample_agent import SampleAgent
from komodo.framework.komodo_workflow import KomodoWorkflow
from komodo.models.framework.workflow_runner import WorkflowRunner


class SampleWorkflow(KomodoWorkflow):
    def __init__(self, path):
        super().__init__(shortcode="sample_workflow", name="Sample Workflow",
                         purpose="Sample workflow to invoke sample agent.")

        agent = SampleAgent(path)
        self.add_node(agent=agent, prompt="Call the sample agent with hello.txt file and call hello_world function.")


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    path = PlatformConfig().komodo_hello_path
    workflow = SampleWorkflow(path)
    print(workflow.to_dict())
    runner = WorkflowRunner(workflow)
    response = runner.run("Run the workflow.")
    print(response.text)
