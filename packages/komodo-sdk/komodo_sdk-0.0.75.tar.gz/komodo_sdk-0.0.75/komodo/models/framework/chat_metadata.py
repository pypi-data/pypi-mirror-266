from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_user import KomodoUser
from komodo.models.framework.models import OPENAI_GPT4_MODEL, OPENAI_GPT35_MODEL


class ChatMetaData:
    def __init__(self, user: KomodoUser, agent: KomodoAgent):
        self.user = user
        self.agent = agent
        self.model = agent.model if agent else OPENAI_GPT35_MODEL

    def max_function_output_len(self):
        return 12000 if self.model == OPENAI_GPT4_MODEL else 6000
