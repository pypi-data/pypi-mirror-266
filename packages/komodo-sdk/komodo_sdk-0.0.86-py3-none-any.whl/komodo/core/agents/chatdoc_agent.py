from komodo.core.tools.files.file_reader import FileReader
from komodo.core.tools.search.vector_search_runtime import VectorSearchTool
from komodo.framework.komodo_agent import KomodoAgent
from komodo.shared.documents.text_extract import to_clean_text


class ChatdocAgent(KomodoAgent):
    shortcode = "chatdoc"
    name = "Documents Agent"
    purpose = "Answers questions based on documents."
    instructions = """
    You are a Document QnA Agent.
    You must answer the questions based on the provided data and tagged with 'Files' below
    The collection and partial file data is provided in the context.
    You should use the vector_search_tool to do semantic search for concepts in the files.
    You can use file_reader tool to read the additional data or specific location in the files.
    
    Make sure that the data returned is relevant to the question else you will be penalized.
    Vector search tool can return inaccurate results. Make sure to validate the results, and use
    file_reader tool at approximate page location to verify the data if necessary.
    
    Do not use any external sources. Do not use your own knowledge.
    Add links to the location within the files: 'komodo://[folder]/[filename]:[position]'
    Only folder and file names must be used in the links. Do not use full paths.
    """

    def __init__(self):
        super().__init__(
            shortcode=self.shortcode,
            name=self.name,
            purpose=self.purpose,
            instructions=to_clean_text(self.instructions))

        self.add_tool(FileReader())
        self.add_tool(VectorSearchTool())
