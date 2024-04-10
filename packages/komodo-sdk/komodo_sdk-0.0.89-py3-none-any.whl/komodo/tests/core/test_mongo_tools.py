from komodo.config import PlatformConfig
from komodo.core.tools.mongo.mongo_connect import get_mongo_client
from komodo.core.tools.mongo.mongo_databases import MongoDBLister
from komodo.core.tools.mongo.mongo_query import MongoDBQuery
from komodo.core.tools.mongo.mongo_schema import MongoDBSchema


def mongo_url():
    return PlatformConfig().get_mongo_url()


def test_mongo_connection_string():
    client = get_mongo_client(mongo_url())
    print(client.list_database_names())
    client.close()


def test_mongo_database_tool():
    mongodb_lister = MongoDBLister(mongo_url())
    result = mongodb_lister.action({"list_collections": True})
    assert result is not None


def test_mongo_query_tool():
    mongodb_query = MongoDBQuery(mongo_url())
    query_args = {
        "database_name": "test_database",
        "collection_name": "posts",
        "query": '{"author": "Mike"}'
    }
    result = mongodb_query.action(query_args)
    print(result)
    assert result is not None


def test_mongo_schema_tool():
    mongodb_schema = MongoDBSchema(mongo_url())
    result = mongodb_schema.action({"database_name": "test_database", "collection_name": "posts"})
    print(result)
    assert result is not None
