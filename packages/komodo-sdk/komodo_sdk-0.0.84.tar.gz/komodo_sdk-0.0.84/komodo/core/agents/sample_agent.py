from komodo.core.tools.utils.sample_tool import SampleTool
from komodo.framework.komodo_agent import KomodoAgent


class SampleAgent(KomodoAgent):
    shortcode = "sample_agent"
    name = "Sample Agent"
    purpose = "Sample agent to invoke sample tool."
    instructions = "Call the sample tool"

    def __init__(self, path):
        super().__init__(shortcode=self.shortcode, name=self.name, purpose=self.purpose,
                         instructions=self.instructions,
                         tools=[SampleTool(path)])
