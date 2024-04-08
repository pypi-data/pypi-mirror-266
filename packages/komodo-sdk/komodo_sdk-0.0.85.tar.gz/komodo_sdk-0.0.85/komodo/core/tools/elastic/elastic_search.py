import fnmatch
import json
from datetime import datetime

from bson import ObjectId
from elastic_transport import ObjectApiResponse

from komodo.core.tools.elastic.elastic_connect import get_elastic_client
from komodo.framework.komodo_tool import KomodoTool


class ElasticQuery(KomodoTool):
    name = "Elastic Query"
    purpose = "Executes a query on elasticsearch cluster and returns the results."
    shortcode = "elastic_query"

    def definition(self, authorized_indexes):
        return {
            "type": "function",
            "function": {
                "name": self.shortcode,
                "description": self.purpose,
                "parameters": {
                    "type": "object",
                    "properties": {
                        "index": {
                            "type": "string",
                            "description": "The index to query. "
                                           "Must be one of the following: " + str(authorized_indexes)
                        },
                        "body": {
                            "type": "string",
                            "description": """
                        The body of the search request string. It MUST be valid json loadable string.
                        e,g. {"query": {"match_all": {}}, "from": 0, "size": 10}
                        The query is executed like this in python client: client.search(index=index, body=body)
                        """
                        },
                        "from": {
                            "type": "integer",
                            "description": "The starting point (offset) from the first result you want to retrieve",
                            "default": 0
                        },
                        "size": {
                            "type": "integer",
                            "description": "The the number of search hits to return. Defaults to 20.",
                            "default": 20
                        }
                    },
                    "required": ["index", "body"]
                },
                "returns": {
                    "type": "string",
                    "description": "The base64 encoded results of the query."
                }
            }
        }

    def __init__(self, connection_string, authorized_indexes):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition(authorized_indexes),
                         action=self.action)
        self.connection_string = connection_string
        self.authorized_indexes = authorized_indexes

    def action(self, args):
        try:
            client = get_elastic_client(self.connection_string)

            # override index to test-* to prevent accidental querying of all indexes
            indexes = []
            for index in args["index"].split(","):
                for authorized in self.authorized_indexes:
                    if fnmatch.fnmatch(index, authorized):
                        indexes.append(index)
                        break
            index = ",".join(indexes)

            body = args["body"]
            offset = args.get("from", 0)
            size = args.get("size", 20)

            # ensure only pageSize number of results are returned
            body = json.loads(body)
            body["from"] = offset
            body["size"] = size

            print(f"Executing Elastic query with {index} and {body}, original index: {args['index']}")
            results = client.search(index=index, body=body)
            client.close()

            # Custom JSON Encoder to handle ObjectId and datetime
            class CustomEncoder(json.JSONEncoder):
                def default(self, obj):
                    if isinstance(obj, ObjectApiResponse):
                        return str(obj)
                    if isinstance(obj, ObjectId):
                        return str(obj)
                    if isinstance(obj, datetime):
                        return obj.isoformat()
                    return json.JSONEncoder.default(self, obj)

            return json.dumps(results, cls=CustomEncoder)

        except Exception as e:
            return "Error: Could not execute Elastic query: " + str(e)
