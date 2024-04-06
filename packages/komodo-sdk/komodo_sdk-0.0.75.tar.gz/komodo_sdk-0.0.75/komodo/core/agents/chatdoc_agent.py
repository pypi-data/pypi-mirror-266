import json

from komodo.core.tools.files.file_reader import FileReader
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext
from komodo.framework.komodo_runtime import KomodoRuntime


class ChatdocAgent(KomodoAgent):
    shortcode = "chatdoc"
    name = "Chat w Documents Agent"
    purpose = "Answers questions based on documents."
    instructions = "You are a Document QnA Agent. " \
                   "You must answer the question based on the provided data. " \
                   "Do not use any external sources."

    def __init__(self):
        super().__init__(
            shortcode=self.shortcode,
            name=self.name,
            purpose=self.purpose,
            instructions=self.instructions)

        self.add_tool(FileReader())

    def generate_context(self, prompt=None, runtime: KomodoRuntime = None):
        context = KomodoContext()
        context.extend(super().generate_context(prompt))
        files = list(runtime.collection.get_files())
        context.add("Files Available", json.dumps(files))
        return context
