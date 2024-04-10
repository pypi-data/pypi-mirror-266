from komodo.framework.komodo_context import KomodoContext
from komodo.framework.komodo_workflow import KomodoWorkflow

from komodo.models.framework.chat_message import ChatMessage


class WorkflowExecutor:
    def __init__(self, prompt, runtime, runner_factory, status_reporter, result_reporter, **kwargs):
        self.runtime = runtime
        self.workflow: [KomodoWorkflow] = runtime.workflow
        self.workflow_goal = prompt
        self.workflow_context: [KomodoContext] = self.build_workflow_context()
        self.kwargs = kwargs

        self.outputs = {}
        self.runner_factory = runner_factory
        self.status_reporter = status_reporter
        self.result_reporter = result_reporter

    def build_workflow_context(self):
        context = KomodoContext()
        context.add("Name", self.workflow.name)
        context.add("Goal", self.workflow_goal)
        context.add("Tags", "All items tagged with Workflow are workflow related content.")
        context.extend(self.workflow.generate_context())
        return context

    def param(self, agent):
        return agent

    def execute(self, agent):
        runner = self.runner_factory(agent, runtime=self.runtime)
        prompt = self.workflow.prompts[agent] if agent in self.workflow.prompts else ""
        self.kwargs.update({'workflow_context': self.workflow_context, 'workflow_inputs': self.inputs(agent)})
        response = runner.run(prompt, **self.kwargs)
        self.outputs[agent.shortcode] = response
        return response

    def inputs(self, agent):
        data = []
        if self.workflow.dag.predecessors(agent):
            message = ChatMessage.build("Purpose", "Feed outputs of the named predecessors to this agent.")
            data.append(message)
            message = ChatMessage.build("Usage",
                                        "Use the outputs of the named predecessors in answering the prompt. "
                                        "Names are enclosed in square brackets, and role is assistant. "
                                        "Do not expose the workflow tags or the names of the workflow predecessors in your response.")
            data.append(message)
            for vertex in self.workflow.dag.predecessors(agent):
                key = vertex.shortcode
                content = self.outputs[key] if key in self.outputs else None
                if content:
                    message = ChatMessage.build(f'[{vertex.name}]', content, role='assistant')
                    data.append(message)

        return data

    def report_start(self, agents):
        if self.status_reporter:
            for agent in agents:
                self.status_reporter(agent, 'Started')

    def report_running(self, agents):
        if self.status_reporter:
            for agent in agents:
                self.status_reporter(agent, 'Running')

    def report_finish(self, agents_result):
        for agent, result in agents_result:
            if self.status_reporter:
                self.status_reporter(agent, 'Finished')

            if self.result_reporter:
                self.result_reporter(agent, result)

    def deliver(self, vertex, result):
        pass  # print('Deliver:', vertex, result)
