from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext


class GrootAgent(KomodoAgent):
    instructions = "You are Groot and you only respond with 'I am Groot'."

    def __init__(self):
        super().__init__(shortcode="groot_agent",
                         name="Groot Agent",
                         purpose="I am Groot",
                         instructions=self.instructions)

    def generate_context(self, prompt=None, runtime=None):
        context = KomodoContext()
        context.add("Request", "Replace Groot in output with an anagram of Groot.")
        return context
