from __future__ import annotations

import typing
from dataclasses import dataclass

import borsh_construct as borsh
from construct import Container

from . import payload


class AuthorizationDataJSON(typing.TypedDict):
    payload: payload.PayloadJSON


@dataclass
class AuthorizationData:
    layout: typing.ClassVar = borsh.CStruct("payload" / payload.Payload.layout)
    payload: payload.Payload

    @classmethod
    def from_decoded(cls, obj: Container) -> "AuthorizationData":
        return cls(payload=payload.Payload.from_decoded(obj.payload))

    def to_encodable(self) -> dict[str, typing.Any]:
        return {"payload": self.payload.to_encodable()}

    def to_json(self) -> AuthorizationDataJSON:
        return {"payload": self.payload.to_json()}

    @classmethod
    def from_json(cls, obj: AuthorizationDataJSON) -> "AuthorizationData":
        return cls(payload=payload.Payload.from_json(obj["payload"]))
