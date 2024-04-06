from komodo.proto.generated.model_pb2 import Agent
from komodo.store.redis_database import RedisDatabase, get_redis_server


class AgentStore:
    def __init__(self, database=RedisDatabase.AGENTS):
        self.redis = get_redis_server(database)

    def add_agent(self, agent):
        agent_data = agent.SerializeToString()
        key = f"agent:{agent.shortcode}"
        self.redis.set(key, agent_data)

    def retrieve_agent(self, shortcode):
        key = f"agent:{shortcode}"
        agent_data = self.redis.get(key)
        if agent_data:
            agent = Agent()  # Make sure Agent is imported from your Protobuf definitions
            agent.ParseFromString(agent_data)
            return agent
        else:
            return None

    def remove_agent(self, shortcode):
        key = f"agent:{shortcode}"
        self.redis.delete(key)
