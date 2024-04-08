from komodo.core.tools.mongo.mongo_connect import get_mongo_client
from komodo.framework.komodo_tool import KomodoTool


class MongoDBUnique(KomodoTool):
    name = "MongoDB Unique Value Finder"
    purpose = "Finds unique values for a specified field within a MongoDB collection."
    shortcode = "mongodb_unique"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "database_name": {
                        "type": "string",
                        "description": "The name of the database."
                    },
                    "collection_name": {
                        "type": "string",
                        "description": "The name of the collection to search for unique values."
                    },
                    "field_name": {
                        "type": "string",
                        "description": "The field for which to find unique values."
                    }
                },
                "required": ["database_name", "collection_name", "field_name"]
            },
            "returns": {
                "type": "string",
                "description": "The unique values found in the specified field, base64 encoded."
            }
        }
    }

    def __init__(self, connection_string):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)
        self.connection_string = connection_string

    def action(self, args):
        try:
            database_name = args["database_name"]
            collection_name = args["collection_name"]
            field_name = args["field_name"]

            client = get_mongo_client(self.connection_string)
            db = client[database_name]
            unique_values = db[collection_name].distinct(field_name)
            client.close()
            return unique_values

        except Exception as e:
            return "Error: Could not find unique values: " + str(e)


if __name__ == "__main__":
    from komodo.config import PlatformConfig

    url = PlatformConfig().get_mongo_url()
    tool = MongoDBUnique(url)
    print(tool.definition)
    print(tool.action({"database_name": "test_database", "collection_name": "posts", "field_name": "author"}))
