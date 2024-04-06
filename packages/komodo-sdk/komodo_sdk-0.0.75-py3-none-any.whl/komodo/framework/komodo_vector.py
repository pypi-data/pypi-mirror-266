
from komodo.shared.utils.digest import get_guid_full


class MetaData:
    def __init__(self, source, chunk, text):
        self.source = source
        self.chunk = chunk
        self.text = text

    def __str__(self):
        return f"MetaData(source={self.source}, chunk={self.chunk}, text={self.text})"

    def __dict__(self):
        return {
            "source": self.source,
            "chunk": self.chunk,
            "text": self.text
        }


class Vector:
    def __init__(self, content, metadata, embedding):
        self.id = get_guid_full()
        self.content = content
        self.metadata = metadata
        self.embedding = embedding

    def __str__(self):
        return f"Vector(id={self.id}, content={self.content}, metadata={self.metadata}, embedding={self.embedding})"

    def __dict__(self):
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "embedding": self.embedding
        }
