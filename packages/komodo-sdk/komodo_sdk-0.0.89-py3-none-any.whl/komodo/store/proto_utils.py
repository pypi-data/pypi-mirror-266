import json

from google.protobuf.json_format import MessageToJson


def convert_proto_to_dict(message):
    if not message:
        return None
    as_json = MessageToJson(message, indent=0).replace("\n", "")
    return json.loads(as_json)
