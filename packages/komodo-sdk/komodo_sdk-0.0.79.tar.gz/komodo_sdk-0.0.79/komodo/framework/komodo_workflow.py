import json

from paradag import DAG

from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext


class KomodoWorkflow:
    def __init__(self, *, shortcode, name, purpose, **kwargs):
        self.shortcode = shortcode
        self.name = name
        self.purpose = purpose
        self.dag = DAG()
        self.prompts: dict[KomodoAgent, str] = {}
        self.context = kwargs.get("context", KomodoContext())
        self.data = kwargs.get("data", {})
        self.dictionary = kwargs.get("dictionary", {})
        self.kwargs = kwargs

    def to_dict(self):
        return {
            "shortcode": self.shortcode,
            "name": self.name,
            "purpose": self.purpose,
            "agents": {a.shortcode: (a.summary(), {'prompt': p}) for a, p in self.nodes_with_prompts()},
            "edges": list((v.shortcode, u.shortcode) for u, v in self.edges()),
            "context": str(self.generate_context())
        }

    def nodes_with_prompts(self):
        for agent, prompt in self.prompts.items():
            yield agent, prompt

    def nodes(self):
        for v in self.dag.vertices():
            yield v

    def edges(self):
        for v in self.dag.vertices():
            for u in self.dag.successors(v):
                yield (v, u)

    def summary(self):
        return {
            "shortcode": self.shortcode,
            "name": self.name,
            "purpose": self.purpose
        }

    def add_node(self, agent, prompt):
        if agent in self.prompts:
            raise ValueError(f"Agent {agent} already exists in workflow. Cannot add it again.")
        self.dag.add_vertex(agent)
        self.prompts[agent] = prompt

    def add_edge(self, agent_from, agent_to):
        self.dag.add_edge(agent_from, agent_to)

    def generate_context(self, prompt=None):
        return self.context

    def explainer(self):
        return KomodoAgent(shortcode=f"{self.shortcode}_explainer",
                           name=f"{self.name} Explainer",
                           purpose="Explain the workflow",
                           instructions="Explain the workflow outputs in a conversational back and forth",
                           context=KomodoContext().add("Workflow Details", json.dumps(self.to_dict())))

    @classmethod
    def default(cls):
        return KomodoWorkflow(shortcode="default_workflow",
                              name="Default Workflow",
                              purpose="A default workflow to demonstrate the capabilities of the appliance.")
