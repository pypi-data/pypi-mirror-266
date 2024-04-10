import fnmatch

from komodo.core.tools.elastic.elastic_connect import get_elastic_client
from komodo.framework.komodo_tool import KomodoTool


class ElasticGet(KomodoTool):
    name = "Elastic Get"
    purpose = "Executes a query on elasticsearch cluster to return a specific object."
    shortcode = "elastic_get"

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
                        "ids": {
                            "type": "string",
                            "description": "Id or ids of the object to retrieve. Separate multiple ids with comma."
                        }
                    },
                    "required": ["index", "ids"]
                },
                "returns": {
                    "type": "str",
                    "description": "The base64 encoded results of the get request."
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

            ids = args["ids"].split(",")

            print(f"Executing Elastic query with {index} and {ids}, original index: {args['index']}")
            if len(ids) == 1:
                result = client.get(index=index, id=ids[0])
            else:
                result = client.mget(index=index, body={"ids": ids})

            client.close()
            return str(result)

        except Exception as e:
            return "Error: Could not execute Elastic query: " + str(e)
