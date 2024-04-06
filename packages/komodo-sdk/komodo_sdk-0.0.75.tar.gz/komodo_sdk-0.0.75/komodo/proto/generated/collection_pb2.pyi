from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class Collection(_message.Message):
    __slots__ = ("shortcode", "name", "description", "path", "created_at", "modified_at", "files", "summary", "query", "questions")
    SHORTCODE_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    FILES_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    QUERY_FIELD_NUMBER: _ClassVar[int]
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    shortcode: str
    name: str
    description: str
    path: str
    created_at: str
    modified_at: str
    files: _containers.RepeatedCompositeFieldContainer[File]
    summary: str
    query: str
    questions: _containers.RepeatedCompositeFieldContainer[QnA]
    def __init__(self, shortcode: _Optional[str] = ..., name: _Optional[str] = ..., description: _Optional[str] = ..., path: _Optional[str] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ..., files: _Optional[_Iterable[_Union[File, _Mapping]]] = ..., summary: _Optional[str] = ..., query: _Optional[str] = ..., questions: _Optional[_Iterable[_Union[QnA, _Mapping]]] = ...) -> None: ...

class File(_message.Message):
    __slots__ = ("guid", "name", "path", "description", "magic", "checksum", "size", "created_at", "modified_at", "indexed_at", "text", "purpose", "summary", "entities", "topics", "toc", "keywords", "questions", "summary_by_section", "summary_by_page", "summary_by_topic", "summary_by_tables", "search_result")
    class SummaryBySectionEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SummaryByPageEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SummaryByTopicEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    class SummaryByTablesEntry(_message.Message):
        __slots__ = ("key", "value")
        KEY_FIELD_NUMBER: _ClassVar[int]
        VALUE_FIELD_NUMBER: _ClassVar[int]
        key: str
        value: str
        def __init__(self, key: _Optional[str] = ..., value: _Optional[str] = ...) -> None: ...
    GUID_FIELD_NUMBER: _ClassVar[int]
    NAME_FIELD_NUMBER: _ClassVar[int]
    PATH_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    MAGIC_FIELD_NUMBER: _ClassVar[int]
    CHECKSUM_FIELD_NUMBER: _ClassVar[int]
    SIZE_FIELD_NUMBER: _ClassVar[int]
    CREATED_AT_FIELD_NUMBER: _ClassVar[int]
    MODIFIED_AT_FIELD_NUMBER: _ClassVar[int]
    INDEXED_AT_FIELD_NUMBER: _ClassVar[int]
    TEXT_FIELD_NUMBER: _ClassVar[int]
    PURPOSE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    ENTITIES_FIELD_NUMBER: _ClassVar[int]
    TOPICS_FIELD_NUMBER: _ClassVar[int]
    TOC_FIELD_NUMBER: _ClassVar[int]
    KEYWORDS_FIELD_NUMBER: _ClassVar[int]
    QUESTIONS_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_BY_SECTION_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_BY_PAGE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_BY_TOPIC_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_BY_TABLES_FIELD_NUMBER: _ClassVar[int]
    SEARCH_RESULT_FIELD_NUMBER: _ClassVar[int]
    guid: str
    name: str
    path: str
    description: str
    magic: str
    checksum: str
    size: int
    created_at: str
    modified_at: str
    indexed_at: str
    text: str
    purpose: str
    summary: str
    entities: str
    topics: str
    toc: str
    keywords: str
    questions: _containers.RepeatedCompositeFieldContainer[QnA]
    summary_by_section: _containers.ScalarMap[str, str]
    summary_by_page: _containers.ScalarMap[str, str]
    summary_by_topic: _containers.ScalarMap[str, str]
    summary_by_tables: _containers.ScalarMap[str, str]
    search_result: SearchResult
    def __init__(self, guid: _Optional[str] = ..., name: _Optional[str] = ..., path: _Optional[str] = ..., description: _Optional[str] = ..., magic: _Optional[str] = ..., checksum: _Optional[str] = ..., size: _Optional[int] = ..., created_at: _Optional[str] = ..., modified_at: _Optional[str] = ..., indexed_at: _Optional[str] = ..., text: _Optional[str] = ..., purpose: _Optional[str] = ..., summary: _Optional[str] = ..., entities: _Optional[str] = ..., topics: _Optional[str] = ..., toc: _Optional[str] = ..., keywords: _Optional[str] = ..., questions: _Optional[_Iterable[_Union[QnA, _Mapping]]] = ..., summary_by_section: _Optional[_Mapping[str, str]] = ..., summary_by_page: _Optional[_Mapping[str, str]] = ..., summary_by_topic: _Optional[_Mapping[str, str]] = ..., summary_by_tables: _Optional[_Mapping[str, str]] = ..., search_result: _Optional[_Union[SearchResult, _Mapping]] = ...) -> None: ...

class SearchResult(_message.Message):
    __slots__ = ("url", "title", "snippet", "source", "summary", "source_date")
    URL_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SNIPPET_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SUMMARY_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DATE_FIELD_NUMBER: _ClassVar[int]
    url: str
    title: str
    snippet: str
    source: str
    summary: str
    source_date: str
    def __init__(self, url: _Optional[str] = ..., title: _Optional[str] = ..., snippet: _Optional[str] = ..., source: _Optional[str] = ..., summary: _Optional[str] = ..., source_date: _Optional[str] = ...) -> None: ...

class QnA(_message.Message):
    __slots__ = ("question", "answer", "title", "snippet", "source", "source_date", "source_url")
    QUESTION_FIELD_NUMBER: _ClassVar[int]
    ANSWER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    SNIPPET_FIELD_NUMBER: _ClassVar[int]
    SOURCE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_DATE_FIELD_NUMBER: _ClassVar[int]
    SOURCE_URL_FIELD_NUMBER: _ClassVar[int]
    question: str
    answer: str
    title: str
    snippet: str
    source: str
    source_date: str
    source_url: str
    def __init__(self, question: _Optional[str] = ..., answer: _Optional[str] = ..., title: _Optional[str] = ..., snippet: _Optional[str] = ..., source: _Optional[str] = ..., source_date: _Optional[str] = ..., source_url: _Optional[str] = ...) -> None: ...
