import json

from komodo.core.tools.files.directory_reader import DirectoryReader
from komodo.core.tools.files.file_reader import FileReader
from komodo.core.tools.search.vector_search import VectorSearch
from komodo.core.utils.indexer import Indexer
from komodo.core.utils.rag_context import RagContext
from komodo.framework.komodo_agent import KomodoAgent
from komodo.framework.komodo_context import KomodoContext


class LibrarianAgent(KomodoAgent):
    shortcode = "librarian"
    name = "Librarian"
    purpose = "Answers questions based on documents."
    instructions = "You are a Document QnA Agent. " \
                   "You will be given vector search tool and a question. " \
                   "You must answer the question based on the provided data. " \
                   "Do not use any external sources."

    def __init__(self, rc: RagContext):
        super().__init__(
            shortcode=self.shortcode + "_" + rc.shortcode,
            name=self.name + f" : {rc.get_display_name()}",
            purpose=self.purpose,
            instructions=self.instructions)

        self.rag_context = rc
        self.files = DirectoryReader().action({'folder': rc.path})
        self.add_tool(FileReader())
        self.add_tool(VectorSearch(rc))

    def generate_context(self, prompt=None, runtime=None):
        context = KomodoContext()
        context.extend(super().generate_context(prompt))
        context.add("Files Available", json.dumps(self.files))
        return context

    def index(self, reindex=False):
        indexer = Indexer(self.rag_context)
        indexer.run(reindex=reindex)
        if reindex:
            self.files = DirectoryReader().action({'folder': self.rag_context.path})
