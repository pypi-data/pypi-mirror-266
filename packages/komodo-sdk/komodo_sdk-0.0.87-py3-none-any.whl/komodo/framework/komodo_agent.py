from komodo.framework.komodo_context import KomodoContext
from komodo.framework.komodo_tool_registry import KomodoToolRegistry
from komodo.models.framework.models import OPENAI_GPT35_MODEL


class KomodoAgent:
    def __init__(self, *, shortcode, name, instructions, **kwargs):
        self.shortcode = shortcode or name.lower().replace(" ", "_")
        self.name = name
        self.instructions = instructions
        self.email = kwargs.get("email", f"{self.shortcode}@kmdo.app")
        self.purpose = kwargs.get("purpose", f"An agent to {instructions}")
        self.model = kwargs.get("model", OPENAI_GPT35_MODEL)
        self.provider = kwargs.get("provider", "openai")

        self.tools = KomodoToolRegistry.get_tools(kwargs.get("tools", []))
        self.max_tokens = kwargs.get("max_tokens")
        self.temperature = kwargs.get("temperature")
        self.seed = kwargs.get("seed")
        self.top_p = kwargs.get("top_p")
        self.output_format = kwargs.get("output_format")

        self.context = kwargs.get("context", KomodoContext())
        self.role = kwargs.get("role")
        self.data = kwargs.get("data", {})
        self.dictionary = kwargs.get("dictionary", {})

        self.autoload_collection = kwargs.get("autoload_collection", True)
        self.max_files_per_request = kwargs.get("max_files_per_request", 10)
        self.max_tokens_per_file = kwargs.get("max_tokens_per_file", 4096)
        self.max_total_tokens = kwargs.get("max_total_tokens", 4096 * 10)

        self.kwargs = kwargs

    def __str__(self):
        return f"KomodoAgent: {self.name} ({self.shortcode}), {self.purpose}"

    def __hash__(self) -> int:
        return hash(self.shortcode)

    def __eq__(self, other):
        if isinstance(other, KomodoAgent):
            return self.shortcode == other.shortcode
        return False

    def to_dict(self):
        return {
            "shortcode": self.shortcode,
            "name": self.name,
            "instructions": self.instructions,
            "email": self.email,
            "purpose": self.purpose,
            "model": self.model,
            "provider": self.provider,
            "tools": [t.to_dict() for t in self.tools],
            "max_tokens": self.max_tokens,
            "temperature": self.temperature,
            "seed": self.seed,
            "top_p": self.top_p,
            "output_format": None
        }

    def summary(self) -> dict:
        return {
            "shortcode": self.shortcode,
            "name": self.name,
            "purpose": self.purpose
        }

    def add_tool(self, tool):
        self.tools.extend(KomodoToolRegistry.get_tools([tool]))
        return self

    def generate_context(self, prompt=None, runtime=None):
        return self.context

    def index(self, reindex=False):
        pass

    @staticmethod
    def default():
        return KomodoAgent(shortcode="komodo", name="Komodo",
                           instructions="Please provide a response to the prompt below.")


if __name__ == '__main__':
    agent = KomodoAgent.default()
    print(agent)
    print(agent.to_dict())
