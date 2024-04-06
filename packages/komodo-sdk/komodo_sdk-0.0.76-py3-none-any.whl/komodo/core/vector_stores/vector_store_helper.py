from langchain_text_splitters import NLTKTextSplitter

from komodo.framework.komodo_vector import MetaData, Vector
from komodo.shared.documents.text_extract import to_clean_text
from komodo.shared.documents.text_extract_helper import TextExtractHelper
from komodo.shared.embeddings.openai import get_embeddings


class VectorStoreHelper:

    def __init__(self, path, cache_path=None):
        self.path = path
        self.cache_path = cache_path
        self.data = None

    def vectorize(self):
        helper = TextExtractHelper(self.path, self.cache_path)
        text = helper.extract_text()
        if text and len(text) > 0:
            self.chunks = self.split_into_chunks(text)
            self.data = self.create_vectors()
            self.update_vector_embeddings(batch_size=100)

    def split_into_chunks(self, text, chunk_size=1200, chunk_overlap=100, pages=20):
        text_splitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
        chunks = text_splitter.split_text(text)
        print("Split text into {} chunks of size: {}".format(len(chunks), chunk_size))
        return chunks

    def create_vectors(self):
        data = []
        for i, chunk in enumerate(self.chunks):
            content = to_clean_text(chunk)
            metadata = MetaData(self.path, i, content)
            vector = Vector(content, metadata, None)
            data.append(vector)
        return data

    def update_vector_embeddings(self, batch_size):
        embeddings_model = get_embeddings()
        for i in range(0, len(self.data), batch_size):
            batch = self.data[i:i + batch_size]
            contents = [item.content for item in batch]
            embeddings = embeddings_model.embed_documents(contents)
            for j, item in enumerate(batch):
                item.embedding = embeddings[j]
        return self.data


if __name__ == '__main__':
    helper = VectorStoreHelper(__file__)
    helper.vectorize()
    print(helper.path)
    print(helper.chunks)
    print(helper.data)
