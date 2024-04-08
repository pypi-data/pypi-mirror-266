from komodo.core.agents.echo_agent import EchoAgent
from komodo.core.agents.groot_agent import GrootAgent
from komodo.core.agents.translator_agent import TranslatorAgent
from komodo.framework.komodo_workflow import KomodoWorkflow


class SampleWorkflow(KomodoWorkflow):
    def __init__(self):
        super().__init__(shortcode="sample_workflow", name="Sample Workflow", purpose="Test out workflows")
        spanish = TranslatorAgent("Spanish")
        french = TranslatorAgent("French")
        groot = GrootAgent()
        echo = EchoAgent()

        self.add_node(spanish, "What is the workflow goal?")
        self.add_node(french, "What is the workflow goal?")
        self.add_node(groot, "Say your name in the language of input from predecessor")
        self.add_node(echo, "Echo what is provided by the agent output above.")
        self.add_edge(spanish, groot)
        self.add_edge(french, echo)


if __name__ == "__main__":
    workflow = SampleWorkflow()
    print(workflow.to_dict())
    print(workflow.explainer().to_dict())
