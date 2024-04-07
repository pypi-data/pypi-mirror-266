from komodo.core.tools.mongo.mongo_connect import get_mongo_client
from komodo.framework.komodo_tool import KomodoTool


class MongoDBSchema(KomodoTool):
    name = "MongoDB Schema Inferer"
    purpose = "Infers the schema of a specified MongoDB collection by sampling documents and analyzing their fields and data types."
    shortcode = "mongodb_schema"

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
                        "description": "The name of the collection to infer the schema for."
                    },
                    "sample_size": {
                        "type": "integer",
                        "description": "The number of documents to sample for schema inference. Defaults to 10.",
                        "default": 10
                    }
                },
                "required": ["database_name", "collection_name"]
            },
            "returns": {
                "type": "string",
                "description": "The inferred schema of the specified collection base64 encoded."
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
            client = get_mongo_client(self.connection_string)
            database_name = args["database_name"]
            collection_name = args["collection_name"]
            sample_size = args.get("sample_size", 10)

            db = client[database_name]
            pipeline = [{"$sample": {"size": sample_size}}, {"$project": {"_id": 0}}]
            samples = list(db[collection_name].aggregate(pipeline))
            client.close()

            schema = {}
            for sample in samples:
                for field in sample:
                    schema[field] = type(sample[field]).__name__

            return schema

        except Exception as e:
            return "Error: Could not infer schema: " + str(e)
