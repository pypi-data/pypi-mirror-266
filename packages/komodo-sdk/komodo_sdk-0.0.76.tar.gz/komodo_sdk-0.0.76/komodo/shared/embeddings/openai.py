from langchain_openai import OpenAIEmbeddings


def get_embeddings() -> OpenAIEmbeddings:
    return OpenAIEmbeddings()
