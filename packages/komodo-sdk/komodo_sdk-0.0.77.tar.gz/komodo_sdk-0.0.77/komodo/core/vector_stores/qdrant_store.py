import json
import os
from time import sleep

from qdrant_client import QdrantClient, models
from qdrant_client.http.models import CollectionInfo

from komodo.framework.komodo_vector import MetaData, Vector
from komodo.framework.komodo_vectorstore import KomodoVectorStore
from komodo.shared.embeddings.openai import get_embeddings

LOCALHOST = 'localhost'

DEFAULT_QDRANT_HOST = LOCALHOST
DEFAULT_QDRANT_PORT = 6333


def get_qdrant_client() -> QdrantClient:
    host = os.getenv('QDRANT_HOST', DEFAULT_QDRANT_HOST)
    port = os.getenv('QDRANT_PORT', DEFAULT_QDRANT_PORT)
    return QdrantClient(host=host, port=port)


class QdrantStore(KomodoVectorStore):

    def __init__(self, shortcode, name, collection_name):
        super().__init__(shortcode, name, type="qdrant")
        self.client = get_qdrant_client()
        self.collection_name = collection_name

    @classmethod
    def create(cls, shortcode):
        name = "Qdrant collection for: " + shortcode
        store = QdrantStore(shortcode, name, shortcode)
        store.get_collection()
        return store

    def get_collection(self) -> CollectionInfo:
        collections = self.client.get_collections()

        # only create collection if it doesn't exist
        if self.collection_name not in [c.name for c in collections.collections]:
            self.client.recreate_collection(
                collection_name=self.collection_name,
                vectors_config=models.VectorParams(
                    size=1536,
                    distance=models.Distance.COSINE,
                ),
            )

        return self.client.get_collection(collection_name=self.collection_name)

    def embeddings(self, text):
        return get_embeddings().embed_query(text)

    def get_count(self):
        return self.client.get_collection(collection_name=self.collection_name).vectors_count

    def print_count(self):
        print(f"Vector count in collection {self.collection_name}: {self.get_count()}")

    def upsert_batched(self, data: [Vector], batch_size=100):
        for i in range(0, len(data), batch_size):
            batch: [Vector] = data[i:i + batch_size]
            if len(batch) > 0:
                ids = [d.id for d in batch]
                embeddings = [d.embedding for d in batch]
                metadatas = [d.metadata.__dict__() for d in batch]
                self.client.upsert(collection_name=self.collection_name,
                                   points=models.Batch(ids=ids, vectors=embeddings, payloads=metadatas))

    def upsert_single(self, id, text, **kwargs):
        embeddings = self.embeddings(text)
        metadata = MetaData(chunk=1, text=text, **kwargs)
        vector = Vector(id, metadata, embeddings)
        self.upsert_batched([vector])

    def upsert_json_list(self, json_list, *, max=1000, **kwargs):
        data_to_upsert = []
        for i, t in enumerate(json_list[:max]):
            s = json.dumps(t)
            metadata = MetaData(chunk=i, text=s, **kwargs)
            embedding = get_embeddings().embed_query(s)
            vector = Vector(s, metadata, embedding)
            data_to_upsert.append(vector)
        self.upsert_batched(data_to_upsert)

    def wait_for_upsert(self, id):
        upserted = False
        while not upserted:
            try:
                self.client.retrieve(self.collection_name, [id])
                upserted = True
                print("Upserted: ", id)
            except Exception as e:
                sleep(1)
                print("Waiting for upsert: " + str(e))
                pass

    def search(self, query, **kwargs) -> list:
        try:
            top_k = kwargs.get("top_k", 5)
            encoded_query = get_embeddings().embed_query(query)

            params = {
                "collection_name": self.collection_name,
                "query_vector": encoded_query,
                "limit": top_k,
            }

            must_filters = []

            if source := kwargs.get("source"):
                must_filters.append(
                    models.FieldCondition(
                        key="source",
                        match=models.MatchText(text=source)  ## we should aim to replace with exact value match
                    )
                )

            if folder := kwargs.get("folder"):
                must_filters.append(
                    models.FieldCondition(
                        key="folder",
                        match=models.MatchValue(value=folder)
                    )
                )

            if filename := kwargs.get("filename"):
                must_filters.append(
                    models.FieldCondition(
                        key="filename",
                        match=models.MatchValue(value=filename)
                    )
                )

            if keywords := kwargs.get("keywords"):
                for k in keywords.split(",") if isinstance(keywords, str) else keywords:
                    must_filters.append(
                        models.FieldCondition(
                            key="text",
                            match=models.MatchText(text=k)
                        )
                    )

            params["query_filter"] = models.Filter(must=must_filters)
            result = self.client.search(**params)  # search qdrant collection for context passage with the answer

            context = [{'id': x.id, 'score': x.score, 'metadata': x.payload} for x in result]
            return context

        except Exception as e:
            print({e})
            return []

    def delete_all_by_source(self, source):
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.FilterSelector(
                    filter=models.Filter(
                        must=[
                            models.FieldCondition(
                                key="source",
                                match=models.MatchValue(value=source),
                            ),
                        ],
                    )
                ),
            )

        except Exception as e:
            print({e})
            return []

    def delete(self, id):
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=models.models.PointIdsList(
                    ids=[id],
                ),
            )

        except Exception as e:
            print({e})
            return []

    def delete_all(self):
        try:
            self.client.delete_collection(collection_name=self.collection_name)
            self.get_collection()
        except Exception as e:
            print({e})
            return []


if __name__ == "__main__":
    store = QdrantStore(shortcode="test", name="Test Store", collection_name="test")
    collection = store.get_collection()
    print(store.to_dict(), collection.dict(), collection.vectors_count)

    store.upsert_single(3, "hello world")
    store.wait_for_upsert(3)
    print(store.search("hello", 3))
    store.delete_all()
    store.print_count()

    store = QdrantStore(shortcode="default", name="Test Store", collection_name="default")
    store.delete_all()
    store.print_count()

    store = QdrantStore(shortcode="sample", name="Test Store", collection_name="sample")
    store.delete_all()
    store.print_count()
