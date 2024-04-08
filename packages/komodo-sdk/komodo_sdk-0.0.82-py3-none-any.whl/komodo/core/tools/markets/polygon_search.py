from komodo.framework.komodo_tool import KomodoTool
from komodo.shared.utils.api_query import do_api_query


class PolygonSearch(KomodoTool):
    name = "Polygon Search Tool"
    purpose = "Leverages Polygon.io to conduct detailed searches across various financial data sources."
    shortcode = "komodo_polygon_search"

    definition = {
        "type": "function",
        "function": {
            "name": shortcode,
            "description": purpose,
            "parameters": {
                "type": "object",
                "properties": {
                    "query_string": {
                        "type": "string",
                        "description": """
                        A fully formed HTTPS query string for the Polygon.io API. 
                        The string should include a placeholder for the API key (YOUR_API_KEY). 
                        e.g. for stocks
                        Daily open close: https://api.polygon.io/v1/open-close/AAPL/YYYY-MM-DD?adjusted=true&apiKey=YOUR_API_KEY
                        Last trade: https://api.polygon.io/v2/last/trade/AAPL?apiKey=YOUR_API_KEY
                        """
                    }
                },
                "required": ["query_string"]
            },
            "output": {
                "type": "string",
                "description": "The output is the response from Polygon.io, formatted using json.dumps. "
                               "It comprises the data requested in the query, in line with the standard response "
                               "structure of Polygon.io."
            },
            "notes": {
                ["Always use the MOST recent data when preparing your response to user.",
                 "For options always know the most recent strike price to keep reporting relevant.",
                 "It supports a wide range of parameters as documented in Polygon.io's guidelines. Downloads data from Polygon.io using a provided HTTPS query string. The function automatically includes an API key, managed by the platform. The response from Polygon.io is returned in a JSON format. In case of error, you must retry by fixing the query string. You must convert any unix timestamps returned to ISO 8601 format for display."]
            }
        }
    }

    def __init__(self, api_key):
        super().__init__(shortcode=self.shortcode,
                         name=self.name,
                         definition=self.definition,
                         action=self.action)
        self.api_key = api_key

    def action(self, args):
        return do_api_query(args, self.api_key)

# Example usage
# args = {"query_string": "https://api.polygon.io/v2/aggs/ticker/AAPL/range/1/day/2020-06-01/2020-06-17?apiKey=API_KEY"}
# data = download_polygon_data(args)
# print(data)
