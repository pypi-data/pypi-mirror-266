import copy
import threading
from time import sleep

from paradag import dag_run, SequentialProcessor, MultiThreadProcessor

from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_runnable import KomodoRunner
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_workflow import KomodoWorkflow
from komodo.models.framework.agent_runner import AgentRunner
from komodo.models.framework.model_response import ModelResponse
from komodo.models.framework.workflow_executor import WorkflowExecutor
from komodo.models.framework.workflow_selector import WorkflowSelector


class WorkflowRunner(KomodoRunner):
    def __init__(self, runtime: KomodoRuntime, parallel=False, max_workers=4):
        super().__init__(runtime=runtime)
        self.workflow: [KomodoWorkflow] = runtime.workflow
        self.user = runtime.user
        self.parallel = parallel
        self.max_workers = max_workers
        self.status = []
        self.outputs = None
        self.text = None

    def status_reporter(self, agent, status):
        # self.status.append(f"{agent.name}: {status}")
        pass

    def result_reporter(self, agent, result):
        prompt = self.workflow.prompts[agent] if agent in self.workflow.prompts else ""
        self.status.append(f"{agent.name}: {prompt} -> {result.text}")

    def run(self, prompt, **kwargs):
        history = kwargs.get('history', None)
        if history:
            explainer = self.workflow.explainer()
            runner = self.runner_factory(explainer, self.runtime)
            return runner.run(prompt, **kwargs)

        else:
            self.status = []
            self.outputs = None

            try:
                processor = SequentialProcessor() if not self.parallel else MultiThreadProcessor()
                selector = WorkflowSelector(max_workers=self.max_workers)
                executor = WorkflowExecutor(prompt, self.runtime, self.runner_factory, self.status_reporter,
                                            self.result_reporter, **kwargs)
                processed = dag_run(self.workflow.dag, processor=processor, executor=executor, selector=selector)
            finally:
                self.status.append("Completed")

            self.outputs = [{agent: executor.outputs[agent.shortcode]} for agent in processed]
            self.text = "\n".join([f"{agent.name}: {executor.outputs[agent.shortcode]}" for agent in processed])

            return ModelResponse(model="Workflow", status="Completed", output=self.outputs, text=self.text)

    def run_streamed(self, prompt, **kwargs):
        history = kwargs.get('history', None)
        if history:
            explainer = self.workflow.explainer()
            runner = self.runner_factory(explainer, self.runtime)
            for response in runner.run_streamed(prompt, **kwargs):
                yield response

        else:
            self.status = []
            self.outputs = None
            r = threading.Thread(target=self.run, args=(prompt,), kwargs=kwargs)
            r.start()

            yielded = 0
            done = False

            while not done:
                n = len(self.status)
                for i in range(yielded, n):
                    done = self.status[i] == "Completed"
                    if not done:
                        yield self.status[i] + "\n\n"

                yielded = n
                if not done:
                    sleep(0.1)

            r.join()

    @staticmethod
    def runner_factory(item, runtime: KomodoRuntime):
        if isinstance(item, KomodoAgent):
            runtime = copy.copy(runtime)
            runtime.set_agent(item)
            return AgentRunner(runtime)
        elif isinstance(item, KomodoWorkflow):
            runtime = copy.copy(runtime)
            runtime.workflow = item
            return WorkflowRunner(runtime)

        raise ValueError(f"Unsupported item type: {type(item)}")
