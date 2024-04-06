from komodo.proto.generated.model_pb2 import Tool
from komodo.store.redis_database import RedisDatabase, get_redis_server


class ToolStore:
    def __init__(self, database=RedisDatabase.TOOLS):
        self.redis = get_redis_server(database)

    def add_tool(self, tool):
        tool_data = tool.SerializeToString()
        key = f"tool:{tool.shortcode}"
        self.redis.set(key, tool_data)

    def retrieve_tool(self, shortcode):
        key = f"tool:{shortcode}"
        tool_data = self.redis.get(key)
        if tool_data:
            tool = Tool()  # Make sure Tool is imported from your Protobuf definitions
            tool.ParseFromString(tool_data)
            return tool
        else:
            return None

    def remove_tool(self, shortcode):
        key = f"tool:{shortcode}"
        self.redis.delete(key)
