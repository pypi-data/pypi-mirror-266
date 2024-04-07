from pathlib import Path

from komodo.config import PlatformConfig
from komodo.core.utils.indexer import Indexer
from komodo.core.utils.rag_context import RagContext
from komodo.core.vector_stores.qdrant_store import QdrantStore
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool import KomodoTool
from komodo.framework.komodo_user import KomodoUser


class VectorSearchTool(KomodoTool):
    name = "Vector Search"
    purpose = "Search available data sources using query or keywords."
    shortcode = "vector_search_tool"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Search across all available data using vector search."
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return, default is 10. Use a minimum value of 5 to find better matches as the search algorithm is evolving.",
                    },
                    "folder": {
                        "type": "string",
                        "description": "Source folder name to search in. Only basename is considered and must be exact match. Default is all folders.",
                    },
                    "filename": {
                        "type": "string",
                        "description": "Source file name to search in. Only basename is considered and must be exact match. Default is all filenames.",
                    },
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Keywords to search for in the text",
                    },
                    "reindex": {
                        "type": "boolean",
                        "description": "Reindex the data if user has requested it, default is False",
                    },
                    "recache": {
                        "type": "boolean",
                        "description": "Recache the data if user has requested it, default is False",
                    },
                },
            }
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)

    def action(self, args, runtime: KomodoRuntime = None):
        # prepare the index for searching
        recache = args.get('recache', False)
        reindex = args.get('reindex', False)

        collection = runtime.selected_collection or runtime.home_folder
        rag_context = RagContext(collection.path, cache_path=runtime.config.cache(), recache=recache)
        indexer = Indexer(rag_context)
        indexer.run(reindex=reindex)

        # do the search
        text = args.get('query')
        if not text:
            return "No search query provided"

        folder = args.get('folder', collection.path.name)
        filename = args.get('filename')
        if not filename and collection.selected_file_guids and len(collection.selected_file_guids) == 1:
            filename = list(collection.get_files())[0].name

        params = {
            "top_k": int(args.get('top_k', 10)),
            "folder": Path(folder).name if folder else None,
            "filename": Path(filename).name if filename else None,
            "keywords": args.get('keywords'),
        }

        result = rag_context.search(text, **params)
        if len(result) > 0:
            return result

        return f"No results found for: {text}, total records: {rag_context.get_count()}"


if __name__ == "__main__":
    def runner():
        store = QdrantStore.create(shortcode="test")
        store.delete_all()
        store.upsert_single(3, "test out this world", source="test123")
        store.upsert_single(3, "test out this forty", source="test123")
        store.wait_for_upsert(3)

        runtime = KomodoRuntime(config=PlatformConfig(), user=KomodoUser.default())
        tool = VectorSearchTool()
        print(tool.definition)
        args = {"query": "test", "top_k": 5, "recache": True, "reindex": True}
        print(tool.action(args, runtime))
        print(tool.action({**args, "source": 'test123'}, runtime))
        print(tool.action({**args, "source": 'test456'}, runtime))
        print(tool.action({**args, "source": 'test123', "keywords": ['engineer']}, runtime))


    runner()
