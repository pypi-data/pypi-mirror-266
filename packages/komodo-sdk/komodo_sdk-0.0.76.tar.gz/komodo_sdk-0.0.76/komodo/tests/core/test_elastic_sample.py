from komodo.shared.utils.digest import get_guid_short

elastic_host = "localhost"
elastic_port = "9200"

from elasticsearch import Elasticsearch

print("Trying to connect to ElasticSearch")
es = Elasticsearch([f"http://{elastic_host}:{elastic_port}"])
print("Connected to ElasticSearch")

# list all the indexes
result = es.cat.indices()
print(result)

result = list(es.indices.get_alias(index="*").keys())
print(result)

es.create(index="test-index", id=get_guid_short(), body={"any": "data", "timestamp": "2021-01-01T00:00:00"})
result = es.search(index="test-index", body={"query": {"match_all": {}}})
print(result)
