from komodo.framework.komodo_tool import KomodoTool


class ChainOfThought(KomodoTool):
    name = "Chain of Thought"
    purpose = "Describe your thinking to the tool"
    shortcode = "chain_of_thought"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "thought": {
                        "type": "string",
                        "description": "Describe your thinking to the tool"
                    }
                },
                "required": ["thought"]
            }
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)

    def action(self, args):
        return "You have described your thinking. Proceed."
