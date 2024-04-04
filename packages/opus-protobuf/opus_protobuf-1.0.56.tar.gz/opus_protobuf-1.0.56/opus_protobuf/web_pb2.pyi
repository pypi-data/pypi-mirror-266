from google.protobuf import empty_pb2 as _empty_pb2
from opus_protobuf import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class CsvFile(_message.Message):
    __slots__ = ("url",)
    URL_FIELD_NUMBER: _ClassVar[int]
    url: str
    def __init__(self, url: _Optional[str] = ...) -> None: ...

class User(_message.Message):
    __slots__ = ("firstName", "lastName", "email", "username", "country", "birthday", "tenant", "industry", "industrySegment", "tags")
    FIRSTNAME_FIELD_NUMBER: _ClassVar[int]
    LASTNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    INDUSTRYSEGMENT_FIELD_NUMBER: _ClassVar[int]
    TAGS_FIELD_NUMBER: _ClassVar[int]
    firstName: str
    lastName: str
    email: str
    username: str
    country: str
    birthday: str
    tenant: str
    industry: str
    industrySegment: str
    tags: str
    def __init__(self, firstName: _Optional[str] = ..., lastName: _Optional[str] = ..., email: _Optional[str] = ..., username: _Optional[str] = ..., country: _Optional[str] = ..., birthday: _Optional[str] = ..., tenant: _Optional[str] = ..., industry: _Optional[str] = ..., industrySegment: _Optional[str] = ..., tags: _Optional[str] = ...) -> None: ...

class Users(_message.Message):
    __slots__ = ("user",)
    USER_FIELD_NUMBER: _ClassVar[int]
    user: _containers.RepeatedCompositeFieldContainer[User]
    def __init__(self, user: _Optional[_Iterable[_Union[User, _Mapping]]] = ...) -> None: ...
