from google.protobuf import empty_pb2 as _empty_pb2
from opus_protobuf import common_pb2 as _common_pb2
from google.protobuf.internal import containers as _containers
from google.protobuf import descriptor as _descriptor
from google.protobuf import message as _message
from typing import ClassVar as _ClassVar, Iterable as _Iterable, Optional as _Optional

DESCRIPTOR: _descriptor.FileDescriptor

class SendValidationCodeEmailRequest(_message.Message):
    __slots__ = ("id", "code")
    ID_FIELD_NUMBER: _ClassVar[int]
    CODE_FIELD_NUMBER: _ClassVar[int]
    id: str
    code: str
    def __init__(self, id: _Optional[str] = ..., code: _Optional[str] = ...) -> None: ...

class SendTalentOpportunityRequest(_message.Message):
    __slots__ = ("id", "talent", "opportunity")
    ID_FIELD_NUMBER: _ClassVar[int]
    TALENT_FIELD_NUMBER: _ClassVar[int]
    OPPORTUNITY_FIELD_NUMBER: _ClassVar[int]
    id: str
    talent: str
    opportunity: str
    def __init__(self, id: _Optional[str] = ..., talent: _Optional[str] = ..., opportunity: _Optional[str] = ...) -> None: ...

class SendCsvReportRequest(_message.Message):
    __slots__ = ("data",)
    DATA_FIELD_NUMBER: _ClassVar[int]
    data: str
    def __init__(self, data: _Optional[str] = ...) -> None: ...

class SendInquireByCulturalAlertRequest(_message.Message):
    __slots__ = ("company", "cultural_alert")
    COMPANY_FIELD_NUMBER: _ClassVar[int]
    CULTURAL_ALERT_FIELD_NUMBER: _ClassVar[int]
    company: str
    cultural_alert: str
    def __init__(self, company: _Optional[str] = ..., cultural_alert: _Optional[str] = ...) -> None: ...

class SendOpportunityEmailNotificationRequest(_message.Message):
    __slots__ = ("id", "subject", "emails", "body", "html")
    ID_FIELD_NUMBER: _ClassVar[int]
    SUBJECT_FIELD_NUMBER: _ClassVar[int]
    EMAILS_FIELD_NUMBER: _ClassVar[int]
    BODY_FIELD_NUMBER: _ClassVar[int]
    HTML_FIELD_NUMBER: _ClassVar[int]
    id: str
    subject: str
    emails: _containers.RepeatedScalarFieldContainer[str]
    body: str
    html: str
    def __init__(self, id: _Optional[str] = ..., subject: _Optional[str] = ..., emails: _Optional[_Iterable[str]] = ..., body: _Optional[str] = ..., html: _Optional[str] = ...) -> None: ...

class SendCulturalAlertInquireRequest(_message.Message):
    __slots__ = ("opportunity", "user")
    OPPORTUNITY_FIELD_NUMBER: _ClassVar[int]
    USER_FIELD_NUMBER: _ClassVar[int]
    opportunity: str
    user: str
    def __init__(self, opportunity: _Optional[str] = ..., user: _Optional[str] = ...) -> None: ...
