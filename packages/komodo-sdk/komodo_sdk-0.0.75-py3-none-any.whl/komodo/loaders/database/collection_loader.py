from komodo.framework.komodo_collection import KomodoCollection
from komodo.store.collection_store import CollectionStore


class CollectionLoader:

    @classmethod
    def load(cls, shortcode, file_guids) -> KomodoCollection:
        collection = CollectionStore().retrieve_collection(shortcode)
        filepaths = [file.path for file in collection.files if file.guid in file_guids]
        return KomodoCollection(shortcode=collection.shortcode, name=collection.name, path=collection.path,
                                description=collection.description, files=filepaths)
