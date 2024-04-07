from komodo import KomodoApp
from komodo.core.agents.chatdoc_agent import ChatdocAgent
from komodo.core.agents.collection_builder import CollectionBuilderAgent
from komodo.core.agents.default import translator_agent, summarizer_agent

from komodo.framework.komodo_context import KomodoContext
from komodo.loaders.filesystem.appliance_loader import ApplianceLoader
from sample.appliance.workflow import SampleWorkflow


class SampleAppliance(KomodoApp):
    shortcode = 'sample'
    name = 'Sample Appliance'
    purpose = 'To test the Komodo Appliances SDK'

    def __init__(self, config):
        base = ApplianceLoader(config.definitions_directory, config.data_directory).load(self.shortcode)
        super().__init__(**base)
        self.config = config

        self.add_agent(summarizer_agent())
        self.add_agent(translator_agent())

        chatdoc = ChatdocAgent()
        chatdoc.max_tokens_per_file = 500
        chatdoc.max_total_tokens = 2000

        self.add_agent(chatdoc)
        self.add_agent(CollectionBuilderAgent())
        self.add_workflow(SampleWorkflow())

    def generate_context(self, prompt=None, runtime=None):
        context = KomodoContext()
        context.add("Sample", f"Develop context for the {self.name} appliance")
        return context
