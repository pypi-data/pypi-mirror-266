import os

from pymongo import MongoClient


def get_mongo_url():
    if os.getenv('MONGO_URL') is None:
        raise ValueError('MONGO_URL environment variable not set')
    return os.getenv('MONGO_URL')


def get_mongo_client(connection_string=None):
    connection_string = connection_string or get_mongo_url()
    return MongoClient(connection_string)
