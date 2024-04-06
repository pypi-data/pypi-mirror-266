from komodo.proto.generated.model_pb2 import User
from komodo.store.redis_database import RedisDatabase, get_redis_server


class UserStore:
    def __init__(self, database=RedisDatabase.USERS):
        self.redis = get_redis_server(database)

    def add_user(self, user):
        user_json = user.SerializeToString()
        key = f"user:{user.email}"
        self.redis.set(key, user_json)

    def retrieve_user(self, email):
        key = f"user:{email}"
        user_json = self.redis.get(key)
        if user_json:
            user = User()
            user.ParseFromString(user_json)
            return user
        else:
            return None

    def remove_user(self, email):
        key = f"user:{email}"
        self.redis.delete(key)


# Example usage
if __name__ == "__main__":
    # Initialize the UserStore with the TEST database
    user_store = UserStore(database=RedisDatabase.TEST)

    # Create a new User object
    user = User(email="test@example.com", name="Test User")

    # Store the user in Redis
    user_store.add_user(user)

    # Retrieve the user from Redis
    retrieved_user = user_store.retrieve_user("test@example.com")
    print("Retrieved User:", retrieved_user.email, retrieved_user.name)

    # Delete the user from Redis
    user_store.remove_user("test@example.com")

    # Try to retrieve the user again to ensure deletion
    deleted_user = user_store.retrieve_user("test@example.com")
    print("Deleted User:", deleted_user)
