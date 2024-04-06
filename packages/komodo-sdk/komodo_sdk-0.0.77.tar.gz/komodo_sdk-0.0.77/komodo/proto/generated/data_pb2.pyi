from google.protobuf.internal import enum_type_wrapper as _enum_type_wrapper
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class DataSource(_message.Message):
    __slots__ = ("name", "type", "filesystem", "webpage", "website", "s3", "database", "api")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[DataSource.Type]
        FILESYSTEM: _ClassVar[DataSource.Type]
        WEBPAGE: _ClassVar[DataSource.Type]
        WEBSITE: _ClassVar[DataSource.Type]
        S3: _ClassVar[DataSource.Type]
        DATABASE: _ClassVar[DataSource.Type]
        API: _ClassVar[DataSource.Type]
    UNSPECIFIED: DataSource.Type
    FILESYSTEM: DataSource.Type
    WEBPAGE: DataSource.Type
    WEBSITE: DataSource.Type
    S3: DataSource.Type
    DATABASE: DataSource.Type
    API: DataSource.Type
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    FILESYSTEM_FIELD_NUMBER: _ClassVar[int]
    WEBPAGE_FIELD_NUMBER: _ClassVar[int]
    WEBSITE_FIELD_NUMBER: _ClassVar[int]
    S3_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    API_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: DataSource.Type
    filesystem: Filesystem
    webpage: Webpage
    website: Website
    s3: S3
    database: Database
    api: Api
    def __init__(self, name: _Optional[str] = ..., type: _Optional[_Union[DataSource.Type, str]] = ..., filesystem: _Optional[_Union[Filesystem, _Mapping]] = ..., webpage: _Optional[_Union[Webpage, _Mapping]] = ..., website: _Optional[_Union[Website, _Mapping]] = ..., s3: _Optional[_Union[S3, _Mapping]] = ..., database: _Optional[_Union[Database, _Mapping]] = ..., api: _Optional[_Union[Api, _Mapping]] = ...) -> None: ...

class Filesystem(_message.Message):
    __slots__ = ("path",)
    PATH_FIELD_NUMBER: _ClassVar[int]
    path: str
    def __init__(self, path: _Optional[str] = ...) -> None: ...

class Webpage(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class Website(_message.Message):
    __slots__ = ("url", "depth")
    URL_FIELD_NUMBER: _ClassVar[int]
    DEPTH_FIELD_NUMBER: _ClassVar[int]
    url: str
    depth: int
    def __init__(self, url: _Optional[str] = ..., depth: _Optional[int] = ...) -> None: ...

class S3(_message.Message):
    __slots__ = ("bucket", "key")
    BUCKET_FIELD_NUMBER: _ClassVar[int]
    KEY_FIELD_NUMBER: _ClassVar[int]
    bucket: str
    key: str
    def __init__(self, bucket: _Optional[str] = ..., key: _Optional[str] = ...) -> None: ...

class Database(_message.Message):
    __slots__ = ("host", "port", "database", "username", "password", "table")
    HOST_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    DATABASE_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    TABLE_FIELD_NUMBER: _ClassVar[int]
    host: str
    port: str
    database: str
    username: str
    password: str
    table: str
    def __init__(self, host: _Optional[str] = ..., port: _Optional[str] = ..., database: _Optional[str] = ..., username: _Optional[str] = ..., password: _Optional[str] = ..., table: _Optional[str] = ...) -> None: ...

class Api(_message.Message):
    __slots__ = ("url", "username", "password")
    URL_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    url: str
    username: str
    password: str
    def __init__(self, url: _Optional[str] = ..., username: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class VectorStore(_message.Message):
    __slots__ = ("name", "type", "index", "pinecone", "qdrant")
    class Type(int, metaclass=_enum_type_wrapper.EnumTypeWrapper):
        __slots__ = ()
        UNSPECIFIED: _ClassVar[VectorStore.Type]
        PINECONE: _ClassVar[VectorStore.Type]
        QDRANT: _ClassVar[VectorStore.Type]
    UNSPECIFIED: VectorStore.Type
    PINECONE: VectorStore.Type
    QDRANT: VectorStore.Type
    NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    INDEX_FIELD_NUMBER: _ClassVar[int]
    PINECONE_FIELD_NUMBER: _ClassVar[int]
    QDRANT_FIELD_NUMBER: _ClassVar[int]
    name: str
    type: str
    index: str
    pinecone: PineconeIndex
    qdrant: QdrantCollection
    def __init__(self, name: _Optional[str] = ..., type: _Optional[str] = ..., index: _Optional[str] = ..., pinecone: _Optional[_Union[PineconeIndex, _Mapping]] = ..., qdrant: _Optional[_Union[QdrantCollection, _Mapping]] = ...) -> None: ...

class PineconeIndex(_message.Message):
    __slots__ = ("name", "dimension", "metric")
    NAME_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    name: str
    dimension: int
    metric: str
    def __init__(self, name: _Optional[str] = ..., dimension: _Optional[int] = ..., metric: _Optional[str] = ...) -> None: ...

class QdrantCollection(_message.Message):
    __slots__ = ("name", "location", "url", "port", "dimension", "metric")
    NAME_FIELD_NUMBER: _ClassVar[int]
    LOCATION_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    PORT_FIELD_NUMBER: _ClassVar[int]
    DIMENSION_FIELD_NUMBER: _ClassVar[int]
    METRIC_FIELD_NUMBER: _ClassVar[int]
    name: str
    location: str
    url: str
    port: int
    dimension: int
    metric: str
    def __init__(self, name: _Optional[str] = ..., location: _Optional[str] = ..., url: _Optional[str] = ..., port: _Optional[int] = ..., dimension: _Optional[int] = ..., metric: _Optional[str] = ...) -> None: ...
