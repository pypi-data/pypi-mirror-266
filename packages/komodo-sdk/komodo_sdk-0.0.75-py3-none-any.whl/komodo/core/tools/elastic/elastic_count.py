import fnmatch
import json

from komodo.core.tools.elastic.elastic_connect import get_elastic_client
from komodo.framework.komodo_tool import KomodoTool


class ElasticCount(KomodoTool):
    name = "Elastic Count"
    purpose = "Executes a query on elasticsearch cluster and returns the count."
    shortcode = "elastic_count"

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
                        }
                    },
                    "required": ["index", "body"]
                },
                "returns": {
                    "type": "integer",
                    "description": "Count of records that match the query in the indexes."
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
            body = json.loads(body)

            print(f"Executing Elastic query with {index} and {body}, original index: {args['index']}")
            result = client.count(index=index, body=body)
            client.close()

            return str(result)

        except Exception as e:
            return "Error: Could not execute Elastic query: " + str(e)
