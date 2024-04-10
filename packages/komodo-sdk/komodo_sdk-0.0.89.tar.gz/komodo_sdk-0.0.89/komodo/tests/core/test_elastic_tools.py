from komodo.config import PlatformConfig
from komodo.core.tools.elastic.elastic_count import ElasticCount
from komodo.core.tools.elastic.elastic_get import ElasticGet
from komodo.core.tools.elastic.elastic_search import ElasticQuery


def elastic_url():
    return PlatformConfig().get_elastic_url()


def authorized_indexes():
    return PlatformConfig().get_authorized_indexes()


def test_elastic_query_tool():
    elastic_query = ElasticQuery(elastic_url(), authorized_indexes())
    query_args = {
        "index": "test-*",  # "test-*" is a wildcard to prevent accidental querying of all indexes
        "body": '{"query": {"match_all": {}}, "from": 0, "size": 10}'
    }
    result = elastic_query.action(query_args)
    print(result)
    assert result is not None


def test_elastic_count_tool():
    elastic_count = ElasticCount(elastic_url(), authorized_indexes())
    query_args = {
        "index": "test-*",  # "test-*" is a wildcard to prevent accidental querying of all indexes
        "body": '{"query": {"match_all": {}}}'
    }
    result = elastic_count.action(query_args)
    print(result)
    assert result is not None


def test_elastic_get_tool():
    elastic_get = ElasticGet(elastic_url(), authorized_indexes())
    query_args = {
        "index": "test-index",  # "test-*" is a wildcard to prevent accidental querying of all indexes
        "ids": "671dd025-8c0a-43db-a916-9ae625a595b6"
    }
    result = elastic_get.action(query_args)
    print(result)
    assert result is not None


def test_elastic_mget_tool():
    elastic_get = ElasticGet(elastic_url(), authorized_indexes())
    query_args = {
        "index": "test-index",  # "test-*" is a wildcard to prevent accidental querying of all indexes
        "ids": "671dd025-8c0a-43db-a916-9ae625a595b6, 671dd025-8c0a-43db-a916-9ae625a595b6"
    }
    result = elastic_get.action(query_args)
    print(result)
    assert result is not None
