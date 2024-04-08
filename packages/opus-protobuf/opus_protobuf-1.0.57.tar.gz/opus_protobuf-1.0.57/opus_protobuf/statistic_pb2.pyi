from google.protobuf import empty_pb2 as _empty_pb2
from opus_protobuf import common_pb2 as _common_pb2
from opus_protobuf import web_pb2 as _web_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Mapping as _Mapping, Optional as _Optional, Union as _Union

DESCRIPTOR: _descriptor.FileDescriptor

class UploadPictureRequest(_message.Message):
    __slots__ = ("userId", "id", "picture")
    USERID_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    PICTURE_FIELD_NUMBER: _ClassVar[int]
    userId: str
    id: str
    picture: _common_pb2.Document
    def __init__(self, userId: _Optional[str] = ..., id: _Optional[str] = ..., picture: _Optional[_Union[_common_pb2.Document, _Mapping]] = ...) -> None: ...

class DataRequest(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class AccessInstagram(_message.Message):
    __slots__ = ("ids", "id", "user", "url", "access_token")
    IDS_FIELD_NUMBER: _ClassVar[int]
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    URL_FIELD_NUMBER: _ClassVar[int]
    ACCESS_TOKEN_FIELD_NUMBER: _ClassVar[int]
    ids: _containers.RepeatedScalarFieldContainer[str]
    id: str
    user: str
    url: str
    access_token: str
    def __init__(self, ids: _Optional[_Iterable[str]] = ..., id: _Optional[str] = ..., user: _Optional[str] = ..., url: _Optional[str] = ..., access_token: _Optional[str] = ...) -> None: ...

class InstagramControllerResponse(_message.Message):
    __slots__ = ("data", "have_mean")
    DATA_FIELD_NUMBER: _ClassVar[int]
    HAVE_MEAN_FIELD_NUMBER: _ClassVar[int]
    data: _containers.RepeatedCompositeFieldContainer[InstagramApiResponse]
    have_mean: bool
    def __init__(self, data: _Optional[_Iterable[_Union[InstagramApiResponse, _Mapping]]] = ..., have_mean: bool = ...) -> None: ...

class InstagramApiResponse(_message.Message):
    __slots__ = ("value", "metadata", "end_time")
    VALUE_FIELD_NUMBER: _ClassVar[int]
    METADATA_FIELD_NUMBER: _ClassVar[int]
    END_TIME_FIELD_NUMBER: _ClassVar[int]
    value: int
    metadata: str
    end_time: str
    def __init__(self, value: _Optional[int] = ..., metadata: _Optional[str] = ..., end_time: _Optional[str] = ...) -> None: ...

class GetInstagramLikesRequest(_message.Message):
    __slots__ = ("data", "broke")
    DATA_FIELD_NUMBER: _ClassVar[int]
    BROKE_FIELD_NUMBER: _ClassVar[int]
    data: AccessInstagram
    broke: bool
    def __init__(self, data: _Optional[_Union[AccessInstagram, _Mapping]] = ..., broke: bool = ...) -> None: ...

class LinkTikTokRequest(_message.Message):
    __slots__ = ("code",)
    CODE_FIELD_NUMBER: _ClassVar[int]
    code: str
    def __init__(self, code: _Optional[str] = ...) -> None: ...

class LinkTensorSocialRequest(_message.Message):
    __slots__ = ("username", "email", "first_name", "last_name", "tenant", "industry", "industry_segment", "country", "birthday", "city")
    USERNAME_FIELD_NUMBER: _ClassVar[int]
    EMAIL_FIELD_NUMBER: _ClassVar[int]
    FIRST_NAME_FIELD_NUMBER: _ClassVar[int]
    LAST_NAME_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    CITY_FIELD_NUMBER: _ClassVar[int]
    username: str
    email: str
    first_name: str
    last_name: str
    tenant: str
    industry: str
    industry_segment: str
    country: str
    birthday: str
    city: str
    def __init__(self, username: _Optional[str] = ..., email: _Optional[str] = ..., first_name: _Optional[str] = ..., last_name: _Optional[str] = ..., tenant: _Optional[str] = ..., industry: _Optional[str] = ..., industry_segment: _Optional[str] = ..., country: _Optional[str] = ..., birthday: _Optional[str] = ..., city: _Optional[str] = ...) -> None: ...

class TalentProfile(_message.Message):
    __slots__ = ("user", "country", "tenant", "industry", "birthday", "industry_segment", "gender")
    USER_FIELD_NUMBER: _ClassVar[int]
    COUNTRY_FIELD_NUMBER: _ClassVar[int]
    TENANT_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_FIELD_NUMBER: _ClassVar[int]
    BIRTHDAY_FIELD_NUMBER: _ClassVar[int]
    INDUSTRY_SEGMENT_FIELD_NUMBER: _ClassVar[int]
    GENDER_FIELD_NUMBER: _ClassVar[int]
    user: str
    country: str
    tenant: str
    industry: str
    birthday: str
    industry_segment: str
    gender: str
    def __init__(self, user: _Optional[str] = ..., country: _Optional[str] = ..., tenant: _Optional[str] = ..., industry: _Optional[str] = ..., birthday: _Optional[str] = ..., industry_segment: _Optional[str] = ..., gender: _Optional[str] = ...) -> None: ...

class TalentMedia(_message.Message):
    __slots__ = ("id", "user", "title", "link", "order", "file")
    ID_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    TITLE_FIELD_NUMBER: _ClassVar[int]
    LINK_FIELD_NUMBER: _ClassVar[int]
    ORDER_FIELD_NUMBER: _ClassVar[int]
    FILE_FIELD_NUMBER: _ClassVar[int]
    id: str
    user: str
    title: str
    link: str
    order: str
    file: _common_pb2.Document
    def __init__(self, id: _Optional[str] = ..., user: _Optional[str] = ..., title: _Optional[str] = ..., link: _Optional[str] = ..., order: _Optional[str] = ..., file: _Optional[_Union[_common_pb2.Document, _Mapping]] = ...) -> None: ...
