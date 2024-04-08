from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool import KomodoTool
from komodo.store.collection_store import CollectionStore


class CollectionReader(KomodoTool):
    name = "Collection Reader Tool"
    purpose = "Read a collection from the database and return file contents and snippets."
    shortcode = "collection_reader"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "shortcode": {
                        "type": "string",
                        "description": "The collection shortcode returned by collection_lister tool."
                    },
                },
                "required": ["shortcode"]
            }
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)

    def action(self, args: dict, runtime: KomodoRuntime):
        store = CollectionStore()
        user = runtime.user
        collections = store.retrieve_collections_by_user(user.email)
        shortcode = args.get('shortcode')
        for c in collections:
            if shortcode in [c.shortcode, c.name, c.path]:
                return store.convert_collection_to_dict(c)

        return "Collection not found."


if __name__ == '__main__':
    lister = CollectionReader()
    runtime = KomodoRuntime()
    print(lister.action({'shortcode': 'xyz'}, runtime))
