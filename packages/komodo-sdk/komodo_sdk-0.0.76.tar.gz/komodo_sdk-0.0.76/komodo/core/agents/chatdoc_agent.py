from komodo.core.tools.files.file_reader import FileReader
from komodo.framework.komodo_agent import KomodoAgent


class ChatdocAgent(KomodoAgent):
    shortcode = "chatdoc"
    name = "Documents Agent"
    purpose = "Answers questions based on documents."
    instructions = "You are a Document QnA Agent. " \
                   "You must answer the questions based on the provided data and tagged with 'Files' below " \
                   "The collection and the file data are provided in the context. " \
                   "You can use file_reader tool to read the additional data from the files. " \
                   "Do not use any external sources."

    def __init__(self):
        super().__init__(
            shortcode=self.shortcode,
            name=self.name,
            purpose=self.purpose,
            instructions=self.instructions)

        self.add_tool(FileReader())
