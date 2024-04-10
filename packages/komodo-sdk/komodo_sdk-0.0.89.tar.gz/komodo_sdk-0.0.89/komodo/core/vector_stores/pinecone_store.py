import json
from time import sleep

from langchain.text_splitter import NLTKTextSplitter
from werkzeug.utils import secure_filename

from komodo.framework.komodo_vectorstore import KomodoVectorStore
from komodo.shared.embeddings.openai import get_embeddings
from komodo.shared.embeddings.pinecone_store import get_pinecone_index, semantic_search


class PineconeStore(KomodoVectorStore):

    def __init__(self, shortcode, name, index):
        super().__init__(shortcode, name, type="pinecone")
        self.index = index

    def get_index(self):
        return get_pinecone_index(self.index)

    def embeddings(self, text):
        return get_embeddings().embed_query(text)

    def upsert(self, id, text, metadata=None):
        index = self.get_index()
        embeddings = self.embeddings(text)
        metadata = metadata or {}
        metadata["text"] = text
        index.upsert(vectors=[{"id": id, "values": embeddings, "metadata": metadata}])

    def wait_for_upsert(self, id):
        index = self.get_index()
        upserted = False
        while not upserted:
            try:
                index.fetch([id])
                upserted = True
                print("Upserted: ", id)
            except Exception as e:
                sleep(1)
                print("Waiting for upsert: " + str(e))
                pass

    def upsert_documents(self, documents, chunk_size=1200, chunk_overlap=100, pages=1000):
        text_splitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        for document in documents:
            text = document.page_content
            texts = text_splitter.split_text(text)
            print("Split text into {} chunks of size: {}".format(len(texts), chunk_size))

            data_to_upsert = []
            for i, t in enumerate(texts[:pages]):
                print("Adding chunk:", i)
                metadata = {}
                metadata["source"] = document.metadata['source'] if document.metadata['source'] else ""
                metadata["title"] = document.metadata['title'] if document.metadata['title'] else ""
                metadata["description"] = document.metadata['description'] if document.metadata['description'] else ""
                metadata["language"] = document.metadata['language'] if document.metadata['language'] else ""
                metadata["chunk"] = i
                metadata["text"] = t
                id = secure_filename(metadata['source']) + f"#chunk_{i}"
                embedding = get_embeddings().embed_query(t)
                data_to_upsert.append({"id": id, "values": embedding, "metadata": metadata})

            if len(data_to_upsert) > 0:
                index = self.get_index()
                index.upsert(vectors=data_to_upsert)

    def upsert_list(self, list, source='', pages=1000):
        data_to_upsert = []
        for i, t in enumerate(list[:pages]):
            print("Adding chunk:", i)
            s = json.dumps(t)

            metadata = {}
            metadata["source"] = source
            metadata["chunk"] = i
            metadata["text"] = s

            id = secure_filename(metadata['source']) + f"#chunk_{i}"
            embedding = get_embeddings().embed_query(s)
            data_to_upsert.append({"id": id, "values": embedding, "metadata": metadata})

        if len(data_to_upsert) > 0:
            index = self.get_index()
            index.upsert(vectors=data_to_upsert)

    def search(self, query, **kwargs) -> list:
        top_k = kwargs.get("top_k", 5)
        results = semantic_search(self.get_index(), query=query, k=top_k)
        output = []
        for match in results['matches']:
            data = {}
            data['id'] = match['id']
            data['score'] = match['score']
            data['metadata'] = match['metadata'] if 'metadata' in match else {}
            output.append(data)
        return output


if __name__ == "__main__":
    store = PineconeStore("test")
    print(store.to_dict())
    store.upsert("3", "hello world", {"foo": "bar"})
    store.wait_for_upsert("3")
    print(store.search("hello", 3))
