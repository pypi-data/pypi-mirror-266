import json

from komodo.core.utils.indexer import Indexer
from komodo.core.utils.rag_context import RagContext
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext


class DifferenceAgent(KomodoAgent):
    shortcode = "difference_agent"
    name = "Document Difference Agent"
    purpose = "Answer questions related to differences in documents."
    instructions = "You are a Difference Agent. You will be given outputs from two sources (Source 1) and (Source 2). " \
                   "You must compare the outputs and provide a meaningful synthesis of the differences between the sources. " \
                   "Do not use any external sources. " \
                   "Use only the information provided by the agents to answer the question."

    def __init__(self, shortcode, rc1: RagContext, rc2: RagContext):
        super().__init__(shortcode=shortcode,
                         name=self.name + f" ({rc1.shortcode}, {rc2.shortcode})",
                         purpose=self.purpose,
                         instructions=self.instructions)
        self.rag_contexts = [rc1, rc2]

    def generate_context(self, prompt=None, runtime=None):
        context = KomodoContext()
        context.extend(super().generate_context(prompt))
        for index, rc in enumerate(self.rag_contexts):
            result = rc.search(prompt)
            context.add(f"Source ({index + 1})",
                        json.dumps(result) if len(result) > 0 else "No results found.")
        return context

    def index(self, reindex=False):
        for rc in self.rag_contexts:
            indexer = Indexer(rc)
            indexer.run(reindex=reindex)
