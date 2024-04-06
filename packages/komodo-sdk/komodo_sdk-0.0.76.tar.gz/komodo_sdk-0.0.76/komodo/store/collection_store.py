import json
from datetime import datetime

from google.protobuf import json_format

from komodo.proto.generated.collection_pb2 import Collection
from komodo.shared.utils.digest import get_guid_short
from komodo.shared.utils.timebox import time_print_simple
from komodo.store.proto_utils import convert_proto_to_dict
from komodo.store.redis_database import RedisDatabase, get_redis_server


class CollectionStore:
    def __init__(self, database=RedisDatabase.COLLECTIONS):
        self.redis = get_redis_server(database)

    def create_collection(self, shortcode, path, name, description):
        print("Creating collection with shortcode: ", shortcode, " name: ", name, " path: ", path)
        shortcode = shortcode or get_guid_short()
        collection = Collection(shortcode=shortcode, name=name, description=description, path=str(path))
        self.store_collection(collection)
        return collection

    def get_or_create_collection(self, shortcode, path, name=None, description=None):
        collection = self.retrieve_collection(shortcode)
        if collection:
            return collection
        else:
            return self.create_collection(shortcode, path, name, description)

    def store_collection(self, collection: Collection):
        collection.modified_at = datetime.utcnow().isoformat() + 'Z'
        collection.created_at = collection.created_at or collection.modified_at
        collection_data = collection.SerializeToString()
        key = f"collection:{collection.shortcode}"
        self.redis.set(key, collection_data)

    def retrieve_collection(self, shortcode):
        key = f"collection:{shortcode}"
        collection_data = self.redis.get(key)
        if collection_data:
            collection = Collection()
            collection.ParseFromString(collection_data)
            return collection
        else:
            print("Collection not found for shortcode: ", shortcode)
            return None

    def retrieve_collection_as_dict(self, shortcode):
        collection = self.retrieve_collection(shortcode)
        return self.convert_collection_to_dict(collection)

    def convert_collection_to_dict(self, collection):
        return convert_proto_to_dict(collection)

    @staticmethod
    def find_file_in_collection(collection, filepath):
        for file in collection.files or []:
            if file.path == str(filepath):
                return file
        return None

    @staticmethod
    def remove_file_in_collection(collection: Collection, filepath):
        for file in collection.files or []:
            if file.path == str(filepath):
                collection.files.remove(file)

    @staticmethod
    def upsert_file_in_collection(collection, file):
        existing = CollectionStore.find_file_in_collection(collection, file.path)
        if existing:
            collection.files.remove(existing)
        collection.files.append(file)

    def remove_collection(self, shortcode):
        key = f"collection:{shortcode}"
        if self.redis.exists(key):
            self.redis.delete(key)

        keys = self.redis.keys(f"user:*:collection:{shortcode}")
        for key in keys:
            self.redis.delete(key)
        keys = self.redis.keys(f"appliance:*:collection:{shortcode}")
        for key in keys:
            self.redis.delete(key)

    def remove_everything(self):
        keys = self.redis.keys("*")
        for key in keys:
            self.redis.delete(key)

    def retrieve_all_collections(self):
        keys = self.redis.keys("collection:*")
        collections = []
        for key in keys or []:
            collection_data = self.redis.get(key)
            collection = Collection()
            collection.ParseFromString(collection_data)
            collections.append(collection)

        return sorted(collections, key=lambda x: x.created_at, reverse=True)

    def add_user_collection(self, user_email, shortcode):
        key = f"user:{user_email}:collection:{shortcode}"
        self.redis.sadd(key, shortcode)

    def remove_user_collection(self, user_email, shortcode):
        key = f"user:{user_email}:collection:{shortcode}"
        self.redis.delete(key)

    def exists_user_collection(self, user_email, shortcode):
        key = f"user:{user_email}:collection:{shortcode}"
        return self.redis.exists(key)

    @time_print_simple
    def retrieve_collections_by_user(self, user_email):
        keys = self.redis.keys(f"user:{user_email}:collection:*")
        collections = []
        for key in keys or []:
            shortcode = key.decode('utf-8').split(":")[-1]
            collection = self.retrieve_collection(shortcode)
            collections.append(collection)

        return sorted(collections, key=lambda x: x.created_at, reverse=True)

    @time_print_simple
    def retrieve_collections_by_user_as_dict(self, user_email):
        collections = self.retrieve_collections_by_user(user_email)
        response = []
        for collection in collections:
            try:
                collection_dict = json.loads(json_format.MessageToJson(collection))
                collection_dict['guid'] = collection.shortcode
                if 'files' in collection_dict:
                    del collection_dict['files']
                response.append(collection_dict)
            except Exception as e:
                print("Failed to list collection with shortcode: ", collection.shortcode, e)
        return response

    def add_appliance_collection(self, appliance_shortcode, shortcode):
        key = f"appliance:{appliance_shortcode}:collection:{shortcode}"
        self.redis.sadd(key, shortcode)

    def remove_appliance_collection(self, appliance_shortcode, shortcode):
        key = f"appliance:{appliance_shortcode}:collection:{shortcode}"
        self.redis.delete(key)

    def exists_appliance_collection(self, appliance_shortcode, shortcode):
        key = f"appliance:{appliance_shortcode}:collection:{shortcode}"
        return self.redis.exists(key)

    def retrieve_collections_by_appliance(self, appliance_shortcode):
        keys = self.redis.keys(f"appliance:{appliance_shortcode}:collection:*")
        collections = []
        for key in keys or []:
            shortcode = key.decode('utf-8').split(":")[-1]
            collection = self.retrieve_collection(shortcode)
            collections.append(collection)
        return collections


if __name__ == "__main__":
    store = CollectionStore(database=RedisDatabase.TEST)
    collection = Collection(name="Test Collection", description="Test Description")
    collection.shortcode = "123"
    collection.path = "test"
    store.store_collection(collection)
    print(store.retrieve_collection("123"))

    user_email = "a@b.com"
    store.add_user_collection(user_email, "123")
    print(store.retrieve_collections_by_user(user_email))

    shortcode = "test"
    store.add_appliance_collection("123", shortcode)
    print(store.retrieve_collections_by_appliance(shortcode))

    collections = store.retrieve_all_collections()
    for collection in collections:
        print(collection)
        print(collection.shortcode)
        store.remove_collection(collection.shortcode)
    print(store.retrieve_all_collections())
    print(store.retrieve_collections_by_user(user_email))
    print(store.retrieve_collections_by_appliance(shortcode))
