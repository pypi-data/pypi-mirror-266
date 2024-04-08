from komodo.core.agents.groot_agent import GrootAgent
from komodo.core.agents.summarizer_agent import SummarizerAgent
from komodo.core.agents.translator_agent import TranslatorAgent
from komodo.framework.komodo_workflow import KomodoWorkflow
from komodo.models.framework.chat_message import ChatMessage
from komodo.models.framework.workflow_runner import WorkflowRunner


def create_test_workflow():
    workflow = KomodoWorkflow(shortcode="groot_workflow", name="Groot Workflow", purpose="Test")
    workflow.context.add("Identity", "Groot")

    groot = GrootAgent()
    summarizer = SummarizerAgent()
    translator_french = TranslatorAgent("French")
    translator_spanish = TranslatorAgent("Spanish")

    workflow.add_node(groot, "Who are you?")
    workflow.add_node(summarizer, "Summarize the Iliad")
    workflow.add_node(translator_french, "Translate output to French")
    workflow.add_node(translator_spanish, "Translate output to Spanish")

    workflow.add_edge(summarizer, translator_french)
    workflow.add_edge(groot, translator_spanish)
    return workflow


def create_test_history():
    history = []
    history.append(ChatMessage(content="Hello", role='user'))
    history.append(ChatMessage(content="How are you?", role='assistant'))
    return history


def create_multilevel_workflow():
    workflow = KomodoWorkflow(shortcode="groot_workflow2", name="Groot Workflow 2", purpose="Test")
    groot = GrootAgent()
    child = create_test_workflow()
    workflow.add_node(groot, "Foo")
    workflow.add_node(child, "Bar")
    workflow.add_edge(groot, child)
    return workflow


def test_groot_workflow():
    workflow = create_test_workflow()
    runner = WorkflowRunner(workflow, parallel=True, max_workers=4)
    results = runner.run("What is the meaning of life?", history=create_test_history())
    print(results.text)


def test_groot_workflow_streamed():
    workflow = create_test_workflow()
    runner = WorkflowRunner(workflow, parallel=True, max_workers=4)
    for status in runner.run_streamed("What is the meaning of life?", history=create_test_history()):
        print(status)
    print(runner.text)


def test_groot_multilevel_workflow():
    workflow = create_multilevel_workflow()
    runner = WorkflowRunner(workflow, parallel=True, max_workers=4)
    results = runner.run("What is the meaning of life?")
    print(results.text)
