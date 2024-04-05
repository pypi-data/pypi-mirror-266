import enum
import typing
from uuid import UUID

import pydantic

from neos_common import base

ResourcePattern = pydantic.constr(pattern=base.ResourceBase.RESOURCE_PATTERN)


class Statement(pydantic.BaseModel):
    model_config = pydantic.ConfigDict(use_enum_values=True)

    sid: str
    principal: typing.Union[list[str], UUID]
    action: list[str]
    resource: list[ResourcePattern]  # type: ignore[reportGeneralTypeIssues]
    condition: list[str] = pydantic.Field(default_factory=list)
    effect: base.EffectEnum

    def is_allowed(self) -> bool:
        return self.effect == base.EffectEnum.allow.value


class PriorityStatement(Statement):
    priority: int


class Statements(pydantic.BaseModel):
    statements: list[Statement]


class PriorityStatements(pydantic.BaseModel):
    statements: list[PriorityStatement]


class SocketRequest(pydantic.BaseModel):
    request_type: str
    data: dict[str, typing.Any]


class PrincipalType(enum.Enum):
    model_config = pydantic.ConfigDict(use_enum_values=True)

    user = "user"
    group = "group"


class Principal(pydantic.BaseModel):
    principal_id: str
    principal_type: PrincipalType


class Principals(pydantic.BaseModel):
    principals: list[Principal]

    def get_principal_ids(self) -> list[str]:
        return [p.principal_id for p in self.principals]


class EventPacket(pydantic.BaseModel):
    source: str
    timestamp: int  # timestamp in ms
    span_id: pydantic.UUID4
    version: str
    message: typing.Union[str, dict[str, typing.Any]]
    message_type: str

    @pydantic.field_validator("span_id")
    def span_id_to_str(cls, value: pydantic.UUID4) -> str:
        return str(value)


class EventPackets(pydantic.BaseModel):
    packets: list[EventPacket]


class ErrorCode(pydantic.BaseModel):
    """Error code."""

    class_name: str
    code: str
    title: str


class ErrorCodes(pydantic.BaseModel):
    """Error codes."""

    errors: list[ErrorCode]
