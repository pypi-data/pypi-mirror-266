from google.protobuf.internal import containers as _containers
from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Report(_message.Message):
    __slots__ = ("guid", "name", "description", "title", "created_at", "modified_at", "widgets")
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    WIDGETS_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    description: str
    title: str
    created_at: str
    modified_at: str
    widgets: _containers.RepeatedCompositeFieldContainer[Widget]
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., title: _Optional[str] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ..., widgets: _Optional[_Iterable[_Union[Widget, _Mapping]]] = ...) -> None: ...

class Widget(_message.Message):
    __slots__ = ("guid", "name", "description", "type", "contents", "audience", "instructions", "created_at", "modified_at")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[Widget.Type]
        TEXT: _ClassVar[Widget.Type]
        SUMMARY: _ClassVar[Widget.Type]
        TABLE: _ClassVar[Widget.Type]
        CHART: _ClassVar[Widget.Type]
        AUDIO: _ClassVar[Widget.Type]
        VIDEO: _ClassVar[Widget.Type]
        IMAGE: _ClassVar[Widget.Type]
        PDF: _ClassVar[Widget.Type]
        HTML: _ClassVar[Widget.Type]
        LINK: _ClassVar[Widget.Type]
        MAP: _ClassVar[Widget.Type]
        DOCUMENT: _ClassVar[Widget.Type]
    UNSPECIFIED: Widget.Type
    TEXT: Widget.Type
    SUMMARY: Widget.Type
    TABLE: Widget.Type
    CHART: Widget.Type
    AUDIO: Widget.Type
    VIDEO: Widget.Type
    IMAGE: Widget.Type
    PDF: Widget.Type
    HTML: Widget.Type
    LINK: Widget.Type
    MAP: Widget.Type
    DOCUMENT: Widget.Type
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    CONTENTS_FIELD_NUMBER: _ClassVar[int]
    AUDIENCE_FIELD_NUMBER: _ClassVar[int]
    INSTRUCTIONS_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    description: str
    type: Widget.Type
    contents: str
    audience: str
    instructions: str
    created_at: str
    modified_at: str
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., type: _Optional[_Union[Widget.Type, str]] = ..., contents: _Optional[str] = ..., audience: _Optional[str] = ..., instructions: _Optional[str] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ...) -> None: ...
