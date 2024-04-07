from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Mode(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
    __slots__ = ()
    MODE_UNSPECIFIED: _ClassVar[Mode]
    MODE_CONVERSATION: _ClassVar[Mode]
    MODE_CHATBOT: _ClassVar[Mode]
    MODE_EMAIL: _ClassVar[Mode]
    MODE_PHONE: _ClassVar[Mode]
    MODE_API: _ClassVar[Mode]
MODE_UNSPECIFIED: Mode
MODE_CONVERSATION: Mode
MODE_CHATBOT: Mode
MODE_EMAIL: Mode
MODE_PHONE: Mode
MODE_API: Mode

class User(_message.Message):
    __slots__ = ("email", "name", "conversations")
    class ConversationsEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    CONVERSATIONS_FIELD_NUMBER: _ClassVar[int]
    email: str
    name: str
    conversations: _containers.ScalarMap[str, str]
    def __init__(self, email: _Optional[str] = ..., name: _Optional[str] = ..., conversations: _Optional[_Mapping[str, str]] = ...) -> None: ...

class Appliance(_message.Message):
    __slots__ = ("shortcode", "name", "purpose", "agent_shortcodes", "tool_shortcodes")
    SHORTCODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    AGENT_SHORTCODES_FIELD_NUMBER: _ClassVar[int]
    TOOL_SHORTCODES_FIELD_NUMBER: _ClassVar[int]
    shortcode: str
    name: str
    purpose: str
    agent_shortcodes: _containers.RepeatedScalarFieldContainer[str]
    tool_shortcodes: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, shortcode: _Optional[str] = ..., name: _Optional[str] = ..., purpose: _Optional[str] = ..., agent_shortcodes: _Optional[_Iterable[str]] = ..., tool_shortcodes: _Optional[_Iterable[str]] = ...) -> None: ...

class Agent(_message.Message):
    __slots__ = ("shortcode", "name", "purpose", "instructions", "model", "provider", "assistant_id", "output_format", "footer", "email", "reply_as", "phone", "tool_shortcodes", "behaviors")
    SHORTCODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    FOOTER_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    REPLY_AS_FIELD_NUMBER: _ClassVar[int]
    PHONE_FIELD_NUMBER: _ClassVar[int]
    TOOL_SHORTCODES_FIELD_NUMBER: _ClassVar[int]
    BEHAVIORS_FIELD_NUMBER: _ClassVar[int]
    shortcode: str
    name: str
    purpose: str
    instructions: str
    model: str
    provider: str
    assistant_id: str
    output_format: str
    footer: str
    email: str
    reply_as: str
    phone: str
    tool_shortcodes: _containers.RepeatedScalarFieldContainer[str]
    behaviors: _containers.RepeatedCompositeFieldContainer[Behavior]
    def __init__(self, shortcode: _Optional[str] = ..., name: _Optional[str] = ..., purpose: _Optional[str] = ..., instructions: _Optional[str] = ..., model: _Optional[str] = ..., provider: _Optional[str] = ..., assistant_id: _Optional[str] = ..., output_format: _Optional[str] = ..., footer: _Optional[str] = ..., email: _Optional[str] = ..., reply_as: _Optional[str] = ..., phone: _Optional[str] = ..., tool_shortcodes: _Optional[_Iterable[str]] = ..., behaviors: _Optional[_Iterable[_Union[Behavior, _Mapping]]] = ...) -> None: ...

class Behavior(_message.Message):
    __slots__ = ("mode", "instructions", "model", "provider", "assistant_id", "output_format", "footer")
    MODE_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    MODEL_FIELD_NUMBER: _ClassVar[int]
    PROVIDER_FIELD_NUMBER: _ClassVar[int]
    ASSISTANT_ID_FIELD_NUMBER: _ClassVar[int]
    OUTPUT_FORMAT_FIELD_NUMBER: _ClassVar[int]
    FOOTER_FIELD_NUMBER: _ClassVar[int]
    mode: Mode
    instructions: str
    model: str
    provider: str
    assistant_id: str
    output_format: str
    footer: str
    def __init__(self, mode: _Optional[_Union[Mode, str]] = ..., instructions: _Optional[str] = ..., model: _Optional[str] = ..., provider: _Optional[str] = ..., assistant_id: _Optional[str] = ..., output_format: _Optional[str] = ..., footer: _Optional[str] = ...) -> None: ...

class Tool(_message.Message):
    __slots__ = ("shortcode", "name", "purpose")
    SHORTCODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    shortcode: str
    name: str
    purpose: str
    def __init__(self, shortcode: _Optional[str] = ..., name: _Optional[str] = ..., purpose: _Optional[str] = ...) -> None: ...

class Conversation(_message.Message):
    __slots__ = ("guid", "title", "created_at", "user_email", "agent_shortcode", "mode", "messages")
    GUID_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    USER_EMAIL_FIELD_NUMBER: _ClassVar[int]
    AGENT_SHORTCODE_FIELD_NUMBER: _ClassVar[int]
    MODE_FIELD_NUMBER: _ClassVar[int]
    MESSAGES_FIELD_NUMBER: _ClassVar[int]
    guid: str
    title: str
    created_at: str
    user_email: str
    agent_shortcode: str
    mode: Mode
    messages: _containers.RepeatedCompositeFieldContainer[Message]
    def __init__(self, guid: _Optional[str] = ..., title: _Optional[str] = ..., created_at: _Optional[str] = ..., user_email: _Optional[str] = ..., agent_shortcode: _Optional[str] = ..., mode: _Optional[_Union[Mode, str]] = ..., messages: _Optional[_Iterable[_Union[Message, _Mapping]]] = ...) -> None: ...

class Message(_message.Message):
    __slots__ = ("guid", "sender", "text", "created_at", "sender_type")
    class SenderType(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[Message.SenderType]
        USER: _ClassVar[Message.SenderType]
        AGENT: _ClassVar[Message.SenderType]
    UNSPECIFIED: Message.SenderType
    USER: Message.SenderType
    AGENT: Message.SenderType
    GUID_FIELD_NUMBER: _ClassVar[int]
    SENDER_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    SENDER_TYPE_FIELD_NUMBER: _ClassVar[int]
    guid: str
    sender: str
    text: str
    created_at: str
    sender_type: Message.SenderType
    def __init__(self, guid: _Optional[str] = ..., sender: _Optional[str] = ..., text: _Optional[str] = ..., created_at: _Optional[str] = ..., sender_type: _Optional[_Union[Message.SenderType, str]] = ...) -> None: ...
