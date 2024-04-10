from komodo.config import PlatformConfig
from komodo.framework.komodo_runtime import KomodoRuntime
from komodo.framework.komodo_tool import KomodoTool
from komodo.framework.komodo_user import KomodoUser
from komodo.store.collection_store import CollectionStore


class CollectionLister(KomodoTool):
    name = "Collection Lister Tool"
    purpose = "Lists all the collections available to the user"
    shortcode = "collection_lister"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
        }
    }

    def __init__(self):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)

    def action(self, args, runtime: KomodoRuntime):
        user = runtime.user
        ## folder = runtime.config.locations().user_collections(user.email)
        ## return {'shortcodes': os.listdir(folder)}
        return CollectionStore().retrieve_collections_by_user_as_dict(user.email)


if __name__ == '__main__':
    config = PlatformConfig()
    user = KomodoUser.default()
    runtime = KomodoRuntime(config=config, user=user)
    lister = CollectionLister()
    print(lister.action({}, runtime))
