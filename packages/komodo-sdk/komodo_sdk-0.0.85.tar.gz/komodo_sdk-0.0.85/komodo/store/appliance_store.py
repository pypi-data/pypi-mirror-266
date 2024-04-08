from komodo.proto.generated.model_pb2 import Appliance
from komodo.store.redis_database import RedisDatabase, get_redis_server


class ApplianceStore:
    def __init__(self, database=RedisDatabase.APPLIANCES):
        self.redis = get_redis_server(database)

    def add_appliance(self, appliance):
        appliance_data = appliance.SerializeToString()
        key = f"appliance:{appliance.shortcode}"
        self.redis.set(key, appliance_data)

    def retrieve_appliance(self, shortcode):
        key = f"appliance:{shortcode}"
        appliance_data = self.redis.get(key)
        if appliance_data:
            appliance = Appliance()  # Ensure Appliance is imported from your Protobuf definitions
            appliance.ParseFromString(appliance_data)
            return appliance
        else:
            return None

    def remove_appliance(self, shortcode):
        key = f"appliance:{shortcode}"
        self.redis.delete(key)
