import unittest

from komodo.shared.utils.digest import get_guid_short
from komodo.store.conversations_store import ConversationStore, RedisDatabase


class TestConversationStore(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # This method will be run once before running all tests
        cls.store = ConversationStore(database=RedisDatabase.CONVERSATIONS)
        cls.user_email = "test@example.com"
        cls.agent_id = "test_agent"
        cls.guid = get_guid_short()

    def test_add_and_retrieve_message(self):
        # Use a specific GUID to test adding and retrieving messages
        conversation_guid_key = f"user:{self.user_email}:agent:{self.agent_id}:guid:{self.guid}"

        # Add a test message
        test_text = "Hello, World!"
        test_sender = "unit_test"
        created_at = "2023-01-01T00:00:00Z"
        self.store.add_message(conversation_guid_key, test_text, test_sender, created_at)

        # Retrieve and verify the message
        messages = self.store.retrieve_messages(conversation_guid_key)
        self.assertEqual(len(messages), 1, "Should retrieve exactly one message")
        self.assertEqual(messages[0]['text'], test_text, "The retrieved message text should match the added message")
        self.assertEqual(messages[0]['sender'], test_sender, "The sender should match")

    @classmethod
    def tearDownClass(cls):
        # Clean up: Remove the conversation and its messages after tests
        conversation_guid_key = f"user:{cls.user_email}:agent:{cls.agent_id}:guid:{cls.guid}"
        cls.store.redis.delete(conversation_guid_key)
        cls.store.remove_conversations(cls.user_email, cls.agent_id)


if __name__ == "__main__":
    unittest.main()
