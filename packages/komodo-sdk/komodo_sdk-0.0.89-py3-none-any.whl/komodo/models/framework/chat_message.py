from komodo.framework.komodo_context import KomodoContext
from komodo.proto.generated.model_pb2 import Message
from komodo.shared.utils.tags import remove_triple_quotes
from komodo.shared.utils.term_colors import print_info


class ChatMessage(dict):
    def __init__(self, content, role="system"):
        dict.__init__(self, role=role, content=content)

    def __getattr__(self, item):
        return super().__getitem__(item)

    def __setattr__(self, item, value):
        return super().__setitem__(item, value)

    def add_tag(self, tag):
        self.content = tag + ": " + self.content
        return self

    @classmethod
    def build(cls, tag, content, role='system'):
        return ChatMessage(tag + ": " + str(content), role)

    @classmethod
    def convert_from_proto_messages(cls, messages):
        return [cls.convert_from_proto(message) for message in messages]

    @classmethod
    def convert_from_proto(cls, message):
        role = "user"
        if message.sender_type == Message.SenderType.AGENT:
            role = "assistant"

        # remove all debug tags
        content = remove_triple_quotes(message.text, "debug")

        # debug messages are not displayed, truncate for logging
        display = content[:96] + " ..." if len(content) > 100 else content
        snippet = display.replace("\n", " ")
        print_info(f'Adding history: role: {role} content: {snippet}')

        return ChatMessage(content, role)

    @classmethod
    def convert_from_context(cls, context: KomodoContext, role='system'):
        return [cls.build(tag, content, role) for tag, content in context.data]
