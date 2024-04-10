from komodo.core.tools.mongo.mongo_connect import get_mongo_client

client = get_mongo_client()
print(client.list_database_names())

db = client.test_database
collection = db.test_collection
import datetime

post = {"author": "Mike",
        "text": "My first blog post!",
        "tags": ["mongodb", "python", "pymongo"],
        "date": datetime.datetime.utcnow()}

posts = db.posts
post_id = posts.insert_one(post).inserted_id
print(post_id)

print(db.list_collection_names())
print(posts.find_one({"author": "Mike"}))
print(posts.find_one({"_id": post_id}))
