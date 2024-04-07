from pathlib import Path

from komodo.shared.utils.digest import get_guid_full


class MetaData:
    def __init__(self, chunk, text, **kwargs):
        self.chunk = chunk
        self.text = text
        self.source = kwargs.pop("source", None)

        folder = kwargs.pop("folder", None)
        self.folder = Path(folder).name if folder else None

        filename = kwargs.pop("filename", None)
        self.filename = Path(filename).name if filename else None
        self.position = kwargs.pop("position", None)

        self.kwargs = kwargs

    def __str__(self):
        return f"MetaData(source={self.source}, chunk={self.chunk}, folder={self.folder}, filename={self.filename}, position={self.position}, text={self.text}, kwargs={self.kwargs})"

    def __dict__(self):
        return {
            "chunk": self.chunk,
            "text": self.text,
            "source": self.source,
            "folder": self.folder,
            "filename": self.filename,
            "position": self.position,
            **self.kwargs
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
