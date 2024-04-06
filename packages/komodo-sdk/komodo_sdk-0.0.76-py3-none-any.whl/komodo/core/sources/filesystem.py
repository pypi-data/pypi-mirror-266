import os

from langchain_community.document_loaders import UnstructuredFileLoader

from komodo.framework.komodo_datasource import KomodoDataSource


class Filesystem(KomodoDataSource):
    def __init__(self, name, source):
        super().__init__(name, type="filesystem")
        self.source = source

    def list_items(self):
        return os.listdir(self.source)

    def list_items_with_details(self):
        from hashlib import md5
        from mmap import mmap, ACCESS_READ

        result = []
        for item in self.list_items():
            path = os.path.join(self.source, item)
            digest = None
            with open(path) as file, mmap(file.fileno(), 0, access=ACCESS_READ) as file:
                digest = md5(file).hexdigest()
            result.append([item, path, os.stat(path), digest])

        return result

    def get_item(self, key):
        path = os.path.join(self.source, key)
        return UnstructuredFileLoader(path).load()
