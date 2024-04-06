import os
from pathlib import Path

from komodo.framework.komodo_context import KomodoContext
from komodo.shared.documents.file_writer_helper import FileWriterHelper
from komodo.shared.documents.text_extract_helper import TextExtractHelper
from komodo.shared.utils.digest import get_num_tokens, get_text_digest_short
from komodo.shared.utils.filestats import file_details, file_details_dict
from komodo.store.collection_store import CollectionStore


class KomodoCollection:
    '''
    KomodoCollection is a class that represents a collection of files. It is used to store and manage collections of files in the Komodo framework. It has the following attributes:
    - shortcode: A string representing the shortcode of the collection.
    - guid: A string representing the guid of the collection.
    - name: A string representing the name of the collection.

    '''

    def __init__(self, *, path, description=None, shortcode=None, name=None, user=None, cache=None):
        self.path = Path(path).absolute()
        print("Path: ", self.path)
        if not self.path.exists() or not self.path.is_dir():
            # create the directory if it doesn't exist
            os.makedirs(self.path, exist_ok=True)
            if not self.path.exists() or not self.path.is_dir():
                raise ValueError(f"Invalid path for collection: {self.path}")

        self.shortcode = shortcode or get_text_digest_short(str(self.path))
        self.guid = self.shortcode

        try:
            store = CollectionStore()
            self.collection = store.get_or_create_collection(self.guid, self.path, name=name, description=description)
            self.collection.summary = "Foo bar test"
            store.store_collection(self.collection)
        except Exception:
            self.collection = None

        # load metadata from collection store if available
        self.name = name or self.collection.name if self.collection else self.path.stem
        self.description = description or self.collection.description if self.collection else None
        self.cache = cache
        self.user = user

    def __str__(self):
        return f"KomodoCollection(name={self.name}, guid={self.guid}, description={self.description})"

    def __eq__(self, other):
        if not isinstance(other, KomodoCollection):
            return False
        return self.guid == other.guid

    def __hash__(self):
        return self.guid

    def get_total_tokens(self) -> int:
        total_tokens = 0
        for file in self.get_files():
            text = self.get_file_text(file)
            total_tokens += get_num_tokens(text)
        return total_tokens

    def get_file_text(self, path: Path):
        return TextExtractHelper(Path(path), cache_path=self.cache).extract_text()

    def get_collection_context(self, max_size=100000):
        context = KomodoContext()
        context.add("Collection Name", self.name)
        files = list(self.get_files())
        total_size = 0
        total_files = len(files)

        for index, file in enumerate(files):
            max_per_file = (max_size - total_size) // (total_files - index)

            text = self.get_file_text(file)
            actual = len(text)
            fitted = actual if actual < max_per_file else max_per_file
            text = text[:fitted]
            total_size += fitted

            context.add(file.stem + " Path", str(file))
            context.add(file.stem + " Contents", text)

            print("Added file to context: ", file.name, " with text length: ", len(text), " actual size: ", actual)

        return context

    def get_collection_summary(self):
        return {
            "name": self.name,
            "description": self.description,
            "files": [f.name for f in self.get_files()]
        }

    def get_collection_summary_for_user(self):
        return "Collection: " + self.name + "\n" + "Description: " + self.description + "\n" + "Files: " + str(
            [f.stem for f in self.get_files()]) + "\n"

    def get_collection_metadata(self):
        attributes = {
            "name": self.name,
            "description": self.description,
            "shortcode": self.shortcode,
            "guid": self.guid,
            "path": str(self.path)
        }

        store = CollectionStore()
        additional = store.retrieve_collection_as_dict(self.guid)
        return {**attributes, **additional}

    def get_collection_with_files(self):
        metadata = self.get_collection_metadata()
        metadata["files"] = [file_details_dict(f) for f in self.get_files()]
        return metadata

    def belongs_to_user(self):
        return self.user and self.user.email in self.path.parts

    def delete_collection(self):
        for f in self.get_files():
            f.unlink()
        self.path.rmdir()
        return {"message": "Successfully deleted collection: " + self.name}

    def add_file(self, filename: str, contents: str, mode: str, existing_behavior: str) -> Path:
        path = self.path / filename
        helper = FileWriterHelper(self.path, filename, mode)
        helper.write_to_file(contents, existing_behavior)
        return path

    def get_files(self):
        for f in self.path.iterdir():
            if f.is_file():
                yield f

    def get_file_metadata(self, filename):
        if path := self.get_file(filename):
            details = file_details(path)
            return {
                "guid": get_text_digest_short(str(path)),
                "name": filename,
                "path": str(path),
                "size": os.path.getsize(path),
                "created_at": os.path.getctime(path),
                "modified_at": os.path.getmtime(path)
            }

    def get_file(self, filename):
        path = self.path / Path(filename).name
        if path.exists():
            return path

    def get_file_by_guid(self, guid):
        for file in self.get_files():
            if get_text_digest_short(str(file)) == guid:
                return file

    def delete_file(self, filename):
        if path := self.get_file(filename):
            path.unlink()
            return {"message": "Successfully deleted file: " + filename}
        return {"message": "File not found: " + filename}


if __name__ == "__main__":
    collection = KomodoCollection(path=".", name="Test Collection", description="Test Collection Description")
    print(collection.path)
    print(collection.shortcode)
    print(collection.get_collection_summary())
    print(collection.get_collection_summary_for_user())
    print(collection.get_collection_metadata())
    # print(collection.get_total_tokens())
