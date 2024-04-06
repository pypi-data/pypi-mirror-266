from elasticsearch import Elasticsearch


def get_elastic_client(connection_string=None):
    return Elasticsearch([connection_string])
