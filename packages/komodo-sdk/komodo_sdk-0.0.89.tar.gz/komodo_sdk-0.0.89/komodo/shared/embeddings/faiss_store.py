from langchain.text_splitter import NLTKTextSplitter
from langchain_community.vectorstores.faiss import FAISS
from langchain_core.documents import Document

from komodo.shared.embeddings.openai import get_embeddings


def init_faiss_db():
    return FAISS.from_texts([""], get_embeddings())


def add_to_faiss(key, text, db, chunk_size=1200, chunk_overlap=100, pages=20):
    print(key)
    name = key.split("/")[-1]
    metadata = {"name": name, 'key': key}

    # Split the source text
    text_splitter = NLTKTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap)
    texts = text_splitter.split_text(text)
    print("Split text into {} chunks of size: {}".format(len(texts), chunk_size))

    docs = [Document(page_content=t, metadata=metadata) for t in texts[:pages]]
    # add to db
    db.add_documents(docs)
