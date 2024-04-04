from google.protobuf import empty_pb2 as _empty_pb2
from opus_protobuf import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class User(_message.Message):
    __slots__ = ("_id", "first_name", "last_name", "email", "type", "profile_picture", "verified", "tenant")
    _ID_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    TYPE_FIELD_NUMBER: _ClassVar[int]
    PROFILE_PICTURE_FIELD_NUMBER: _ClassVar[int]
    VERIFIED_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    _id: str
    first_name: str
    last_name: str
    email: str
    type: UserType
    profile_picture: _common_pb2.Document
    verified: bool
    tenant: _containers.RepeatedScalarFieldContainer[str]
    def __init__(self, _id: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., email: _Optional[str] = ..., type: _Optional[_Union[UserType, _Mapping]] = ..., profile_picture: _Optional[_Union[_common_pb2.Document, _Mapping]] = ..., verified: bool = ..., tenant: _Optional[_Iterable[str]] = ...) -> None: ...

class UserType(_message.Message):
    __slots__ = ("_id", "label")
    _ID_FIELD_NUMBER: _ClassVar[int]
    LABEL_FIELD_NUMBER: _ClassVar[int]
    _id: str
    label: str
    def __init__(self, _id: _Optional[str] = ..., label: _Optional[str] = ...) -> None: ...

class CreateTalentOpportunityRequest(_message.Message):
    __slots__ = ("user", "talent", "opportunity")
    USER_FIELD_NUMBER: _ClassVar[int]
    TALENT_FIELD_NUMBER: _ClassVar[int]
    OPPORTUNITY_FIELD_NUMBER: _ClassVar[int]
    user: str
    talent: str
    opportunity: str
    def __init__(self, user: _Optional[str] = ..., talent: _Optional[str] = ..., opportunity: _Optional[str] = ...) -> None: ...

class CreateTalentOpportunityResponse(_message.Message):
    __slots__ = ("accepted", "company", "talent", "opportunity")
    ACCEPTED_FIELD_NUMBER: _ClassVar[int]
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    TALENT_FIELD_NUMBER: _ClassVar[int]
    OPPORTUNITY_FIELD_NUMBER: _ClassVar[int]
    accepted: bool
    company: str
    talent: str
    opportunity: str
    def __init__(self, accepted: bool = ..., company: _Optional[str] = ..., talent: _Optional[str] = ..., opportunity: _Optional[str] = ...) -> None: ...

class GetShortLinkRequest(_message.Message):
    __slots__ = ("slug",)
    SLUG_FIELD_NUMBER: _ClassVar[int]
    slug: str
    def __init__(self, slug: _Optional[str] = ...) -> None: ...
