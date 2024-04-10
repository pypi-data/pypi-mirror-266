from komodo.framework.komodo_agent import KomodoAgent


class EchoAgent(KomodoAgent):
    instructions = "You echo what is provided as input."

    def __init__(self):
        super().__init__(shortcode="echo_agent",
                         name="Echo Agent",
                         purpose="Echo what is provided as input.",
                         instructions=self.instructions)
