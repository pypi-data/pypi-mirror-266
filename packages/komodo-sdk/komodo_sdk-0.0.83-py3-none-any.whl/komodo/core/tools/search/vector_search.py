from komodo.core.vector_stores.qdrant_store import QdrantStore
from komodo.framework.komodo_tool import KomodoTool
from komodo.framework.komodo_vectorstore import KomodoVectorSearcher


class VectorSearch(KomodoTool):
    name = "Vector Search"
    purpose = "Search available data sources"
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
                        "description": "Search across all available data using vector search"
                    },
                    "top_k": {
                        "type": "integer",
                        "description": "Number of results to return, default is 3",
                    },
                    "source": {
                        "type": "string",
                        "description": "Source file name to search in. Default is all sources.",
                    },
                    "keywords": {
                        "type": "array",
                        "items": {
                            "type": "string"
                        },
                        "description": "Keywords to search for in the text",
                    }
                },
                "required": ["query"]
            }
        }
    }

    def __init__(self, searcher: KomodoVectorSearcher):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)
        self.searcher = searcher

    def action(self, args):
        text = args['query']
        params = {
            "top_k": int(args.get('top_k', 3)),
            "source": args.get('source'),
            "keywords": args.get('keywords'),
        }

        result = self.searcher.search(text, **params)
        if len(result) > 0:
            return result
        return f"No results found for: {text}, total records: {self.searcher.get_count()}"


if __name__ == "__main__":
    store = QdrantStore.create(shortcode="test")
    store.delete_all()
    store.upsert_single(3, "test out this world", source="test123")
    store.upsert_single(3, "test out this forty", source="test123")
    store.wait_for_upsert(3)

    tool = VectorSearch(store)
    print(tool.definition)
    print(tool.action({"query": "test", "top_k": 5}))
    print(tool.action({"query": "test", "top_k": 5, "source": 'test123'}))
    print(tool.action({"query": "test", "top_k": 5, "source": 'test456'}))
    print(tool.action({"query": "test", "top_k": 5, "source": 'test123', "keywords": ['world']}))
