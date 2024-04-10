from google.protobuf import empty_pb2 as _empty_pb2
from opus_protobuf import user_pb2 as _user_pb2
from opus_protobuf import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class LoginRequest(_message.Message):
    __slots__ = ("email", "password")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ...) -> None: ...

class SignupRequest(_message.Message):
    __slots__ = ("email", "password", "first_name", "last_name", "type")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    PASSWORD_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    email: str
    password: str
    first_name: str
    last_name: str
    type: str
    def __init__(self, email: _Optional[str] = ..., password: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class JWTResponse(_message.Message):
    __slots__ = ("token",)
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    token: str
    def __init__(self, token: _Optional[str] = ...) -> None: ...

class SignupGoogleRequest(_message.Message):
    __slots__ = ("token", "type")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    token: str
    type: str
    def __init__(self, token: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class SignupAppleRequest(_message.Message):
    __slots__ = ("token", "type")
    TOKEN_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    token: str
    type: str
    def __init__(self, token: _Optional[str] = ..., type: _Optional[str] = ...) -> None: ...

class TalentProfileCreateCsvRequest(_message.Message):
    __slots__ = ("email", "birthday", "tenant", "industry", "industry_segment", "country", "city", "gender", "user", "description")
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    DESCRIPTION_FIELD_NUMBER: _ClassVar[int]
    email: str
    birthday: str
    tenant: _containers.RepeatedScalarFieldContainer[str]
    industry: _containers.RepeatedScalarFieldContainer[str]
    industry_segment: _containers.RepeatedScalarFieldContainer[str]
    country: str
    city: str
    gender: str
    user: str
    description: str
    def __init__(self, email: _Optional[str] = ..., birthday: _Optional[str] = ..., tenant: _Optional[_Iterable[str]] = ..., industry: _Optional[_Iterable[str]] = ..., industry_segment: _Optional[_Iterable[str]] = ..., country: _Optional[str] = ..., city: _Optional[str] = ..., gender: _Optional[str] = ..., user: _Optional[str] = ..., description: _Optional[str] = ...) -> None: ...
