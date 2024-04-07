from komodo.framework.komodo_vector import Vector


class KomodoVectorSearcher():

    def search(self, text, **kwargs):
        raise NotImplementedError

    def get_count(self):
        raise NotImplementedError


class KomodoVectorStore(KomodoVectorSearcher):
    def __init__(self, shortcode, name, type):
        self.shortcode = shortcode
        self.name = name
        self.type = type

    def __str__(self):
        return f"{self.name} ({self.shortcode}, {self.type})"

    def to_dict(self):
        return {
            "shortcode": self.shortcode,
            "name": self.name,
            "type": self.type,
        }

    def embeddings(self, text):
        raise NotImplementedError

    def upsert_batched(self, data: [Vector], batch_size=100):
        raise NotImplementedError

    def upsert_single(self, id, text, source='Unknown'):
        raise NotImplementedError

    def upsert_json_list(self, json_list, source='Unknown', max=1000):
        raise NotImplementedError

    def wait_for_upsert(self, id):
        raise NotImplementedError

    def search(self, text, **kwargs):
        raise NotImplementedError

    def get_count(self):
        raise NotImplementedError

    def delete(self, id):
        raise NotImplementedError

    def delete_all(self):
        raise NotImplementedError
