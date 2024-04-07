import os
from pathlib import Path

from komodo.core.vector_stores.qdrant_store import QdrantStore
from komodo.core.vector_stores.vector_store_helper import VectorStoreFileHelper
from komodo.framework.komodo_vectorstore import KomodoVectorSearcher
from komodo.shared.utils.digest import get_text_digest_short
from komodo.shared.utils.term_colors import print_info
from komodo.store.collection_store import CollectionStore


class RagContext(KomodoVectorSearcher):
    def __init__(self, path, *, cache_path, shortcode=None, recache=False):
        self.shortcode = get_text_digest_short(str(path)) if shortcode is None else shortcode
        self.path = Path(path).absolute()
        self.cache_path = cache_path
        self.recache = recache
        print(f"Created Rag Context: Folder: {path} Cache: {cache_path} Shortcode: {self.shortcode}")

    def get_display_name(self):
        return os.path.basename(self.path)

    def get_rag_collection(self):
        collection_store = CollectionStore()
        name = os.path.basename(self.path)
        description = f"Collection for {name}"
        return collection_store.get_or_create_collection(shortcode=self.shortcode, path=self.path, name=name,
                                                         description=description)

    def find_file(self, filepath):
        print("Searching for: " + filepath + " in collection: " + self.shortcode)
        collection = self.get_rag_collection()
        collection_store = CollectionStore()
        return collection_store.find_file_in_collection(collection, filepath)

    def update_file(self, filepath, file):
        print("Updating: " + filepath + " in collection: " + self.shortcode)
        collection = self.get_rag_collection()
        collection_store = CollectionStore()
        collection_store.upsert_file_in_collection(collection, file)
        collection_store.store_collection(collection)

    def index(self, filepath):
        print("Indexing: " + filepath + " into collection: " + self.shortcode)
        helper = VectorStoreFileHelper(filepath, self.cache_path, self.recache)
        try:
            helper.vectorize()
            if data := helper.data:
                print("Vectors are being created for file: " + filepath)
                self.get_vector_store().upsert_batched(data)
            else:
                print("Vectors could not be created for: " + filepath)
        except Exception as e:
            print("Error indexing: " + filepath)
            print(e)

    def get_vector_store(self):
        return QdrantStore.create(self.shortcode)

    def search(self, text, **kwargs):
        print_info(f"Searching collection: {self.shortcode} for: {text} with args: {kwargs}")
        return self.get_vector_store().search(text, **kwargs)

    def get_count(self):
        return self.get_vector_store().get_count()

    def remove(self, filepath):
        print("Removing: " + filepath + " from rag context: " + self.shortcode)
        print("Removing from index: " + filepath)
        self.get_vector_store().delete_all_by_source(filepath)

        print("Removing from collection: " + filepath)
        file = self.find_file(filepath)
        if file:
            collection = self.get_rag_collection()
            collection.files.remove(file)
            collection_store = CollectionStore()
            collection_store.store_collection(collection)

    def reset_all(self):
        self.get_vector_store().delete_all()
        collection_store = CollectionStore()
        collection_store.remove_collection(self.shortcode)
