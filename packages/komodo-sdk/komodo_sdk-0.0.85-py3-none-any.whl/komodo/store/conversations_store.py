import json
from datetime import datetime

from google.protobuf import json_format

from komodo.proto.generated.model_pb2 import Conversation, Message
from komodo.shared.utils.digest import get_guid_short
from komodo.store.redis_database import RedisDatabase, get_redis_server


class ConversationStore:
    def __init__(self, database=RedisDatabase.CONVERSATIONS):
        self.redis = get_redis_server(database)

    def get_or_create_conversation(self, guid, agent_shortcode, email, prompt):
        if guid:
            header_key = f"guid:{guid}:conversation"
            header = self.redis.get(header_key)
            if header:
                return self.get_conversation(guid)

        title = prompt
        return self.create_conversation(guid, email, agent_shortcode, title)

    def add_conversation_guid(self, user_email, agent_shortcode, guid):
        key = f"user:{user_email}:agent:{agent_shortcode}"
        self.redis.sadd(key, guid)

    def add_header(self, guid, title, created_at, user_email, agent_shortcode):
        conversation = Conversation(guid=guid, title=title, created_at=created_at, user_email=user_email,
                                    agent_shortcode=agent_shortcode)
        header_data = conversation.SerializeToString()
        header_key = f"guid:{guid}:conversation"
        self.redis.set(header_key, header_data)
        return conversation

    def add_message(self, guid, sender, sender_type, text):
        now = datetime.utcnow().isoformat() + 'Z'
        message = Message(guid=get_guid_short(), sender_type=sender_type, sender=sender,
                          text=text, created_at=now)
        message_data = message.SerializeToString()
        messages_key = f"guid:{guid}:messages"
        self.redis.rpush(messages_key, message_data)

    def add_user_message(self, guid, sender, text):
        self.add_message(guid, sender, Message.SenderType.USER, text)

    def add_agent_message(self, guid, sender, text):
        self.add_message(guid, sender, Message.SenderType.AGENT, text)

    def create_conversation(self, conversation_guid, user_email, agent_shortcode, title):
        now = datetime.utcnow().isoformat() + 'Z'
        conversation_guid = conversation_guid or get_guid_short()
        self.add_conversation_guid(user_email, agent_shortcode, conversation_guid)
        conversation = self.add_header(conversation_guid, title, now, user_email, agent_shortcode)
        return conversation

    def get_conversation_header(self, guid):
        header_key = f"guid:{guid}:conversation"
        conversation = self.redis.get(header_key)
        conv = Conversation()
        conv.ParseFromString(conversation)
        conv_dict = json.loads(json_format.MessageToJson(conv))
        return conv_dict

    # Method to retrieve conversation GUIDs
    def retrieve_conversation_guids(self, user_email, agent_shortcode):
        key = f"user:{user_email}:agent:{agent_shortcode}"
        guids = self.redis.smembers(key)
        # Decode each guid from bytes to string
        decoded_guids = [guid.decode('utf-8') for guid in guids]
        return decoded_guids

    def get_conversation(self, guid):
        header_key = f"guid:{guid}:conversation"
        conversation = self.redis.get(header_key)
        conv = Conversation()
        conv.ParseFromString(conversation)
        conv.messages.extend(self.get_messages(guid))
        return conv

    def get_conversation_as_dict(self, guid):
        conversation_header = self.get_conversation_header(guid)
        conversation_messages = self.get_messages_as_dict(guid)
        # Modify here to wrap the response in a list to match the array structure
        conversation_data = [{
            "conversation": conversation_header,
            "messages": conversation_messages
        }]
        return conversation_data

    def get_conversation_headers(self, user_email, agent_shortcode):
        conversations_data = []
        conversation_guids = self.retrieve_conversation_guids(user_email, agent_shortcode)
        for guid in conversation_guids:
            conv_data = self.get_conversation_header(guid)
            conversations_data.append(conv_data)
        return conversations_data

    # Method to retrieve messages for a specific conversation
    def get_messages(self, conversation_guid):
        messages_key = f"guid:{conversation_guid}:messages"
        messages_data = self.redis.lrange(messages_key, 0, -1)
        messages = []
        for msg_data in messages_data:
            msg = Message()
            msg.ParseFromString(msg_data)
            messages.append(msg)
        return messages

    def get_messages_as_dict(self, conversation_guid):
        messages = self.get_messages(conversation_guid)
        messages_data = []
        for msg in messages:
            msg_dict = json.loads(json_format.MessageToJson(msg))
            messages_data.append(msg_dict)
        return messages_data

    def delete_conversation(self, guid, user_email):
        messages_key = f"guid:{guid}:messages"
        self.redis.delete(messages_key)

        conv_header_data = self.get_conversation_header(guid)
        header_key = f"guid:{guid}:conversation"
        self.redis.delete(header_key)

        print(conv_header_data)

        # Remove the GUID from the set of conversations for the user-agent pair in the CONVERSATIONS database
        agent_shortcode = conv_header_data['agentShortcode']
        conversation_key = f"user:{user_email}:agent:{agent_shortcode}"
        self.redis.srem(conversation_key, guid)

        return {
            "guid": guid,
            "success": True,
            "message": "Deleted the conversation successfully"
        }
