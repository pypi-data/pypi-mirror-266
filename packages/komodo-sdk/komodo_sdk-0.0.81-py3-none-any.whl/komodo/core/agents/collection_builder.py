from komodo.core.tools.files.collection_builder import CollectionBuilder
from komodo.core.tools.files.collection_lister import CollectionLister
from komodo.core.tools.files.collection_reader import CollectionReader
from komodo.core.tools.files.directory_reader import DirectoryReader
from komodo.core.tools.files.file_reader import FileReader
from komodo.core.tools.files.file_writer import FileWriter
from komodo.framework.komodo_agent import KomodoAgent


class CollectionBuilderAgent(KomodoAgent):
    instructions = "Use the collection_builder tool to build collections, and answer questions on files in those collections. " \
                   "After you build the collection, you should read the directory contents to get the latest files. " \
                   "Use collection_lister and collection_reader to get information about the files. " \
                   "User file_reader to read files, and file_writer to write files."

    def __init__(self):
        super().__init__(shortcode="collection_agent",
                         name="Auto Researcher",
                         purpose="Builds content on topics of interest",
                         instructions=self.instructions)

        self.add_tool(CollectionBuilder())
        self.add_tool(CollectionLister())
        self.add_tool(CollectionReader())
        self.add_tool(DirectoryReader())
        self.add_tool(FileReader())
        self.add_tool(FileWriter())
