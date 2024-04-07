from pathlib import Path

from langchain_text_splitters import NLTKTextSplitter

from komodo.framework.komodo_vector import MetaData, Vector
from komodo.shared.documents.text_extract_helper import TextExtractHelper
from komodo.shared.embeddings.openai import get_embeddings
from komodo.shared.utils.term_colors import print_gray


class VectorStoreFileHelper:

    def __init__(self, path, cache_path=None, recache=False):
        self.path = Path(path)
        self.cache_path = Path(cache_path)
        self.recache = recache
        self.data = None
        self.chunk_size = 1200
        self.chunk_overlap = 100

    def vectorize(self):
        helper = TextExtractHelper(self.path, self.cache_path, self.recache)
        text = helper.extract_text()
        if text and len(text) > 0:
            self.chunks = self.split_into_chunks(text)
            self.data = self.create_vectors()
            self.update_vector_embeddings(batch_size=100)

    def split_into_chunks(self, text):
        text_splitter = NLTKTextSplitter(chunk_size=self.chunk_size, chunk_overlap=self.chunk_overlap)
        chunks = text_splitter.split_text(text)
        print_gray("Split text into {} chunks of target size: {}".format(len(chunks), self.chunk_size))
        return chunks

    def create_vectors(self):
        data = []
        for i, chunk in enumerate(self.chunks):
            metadata = MetaData(chunk=i, text=chunk, folder=self.path.parent, filename=self.path.name,
                                source=str(self.path.absolute()), position=i * self.chunk_size)
            vector = Vector(chunk, metadata, None)
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
    helper = VectorStoreFileHelper(__file__)
    helper.vectorize()
    print(helper.path)
    print(helper.chunks)
    print(helper.data)
