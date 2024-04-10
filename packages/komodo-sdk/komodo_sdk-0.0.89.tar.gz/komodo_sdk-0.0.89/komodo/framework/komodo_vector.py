from komodo.shared.utils.digest import get_guid_from_string


class MetaData:
    def __init__(self, chunk, text, **kwargs):
        self.chunk = chunk
        self.text = text
        self.kwargs = kwargs

    def __str__(self):
        return f"Metadata({self.__dict__()})"

    def __dict__(self):
        return {
            "chunk": self.chunk,
            "text": self.text,
            **self.kwargs
        }


class Vector:
    def __init__(self, content, metadata, embedding):
        self.id = content if isinstance(content, int) else get_guid_from_string(str(content))
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


class SearchResult:
    def __init__(self, id, score, metadata):
        self.id = id
        self.score = score
        self.metadata = metadata

    def __str__(self):
        return f"SearchResult(id={self.id}, score={self.score}, metadata={self.metadata})"

    def __dict__(self):
        return {
            "id": self.id,
            "score": self.score,
            "metadata": self.metadata
        }
