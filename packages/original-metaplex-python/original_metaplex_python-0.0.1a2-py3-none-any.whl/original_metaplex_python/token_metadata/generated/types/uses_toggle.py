from __future__ import annotations

import typing
from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import EnumForCodegen

from . import uses

SetJSONValue = tuple[uses.UsesJSON]
SetValue = tuple[uses.Uses]


class NoneJSON(typing.TypedDict):
    kind: typing.Literal["None"]


class ClearJSON(typing.TypedDict):
    kind: typing.Literal["Clear"]


class SetJSON(typing.TypedDict):
    value: SetJSONValue
    kind: typing.Literal["Set"]


@dataclass
class None_:
    discriminator: typing.ClassVar = 0
    kind: typing.ClassVar = "None"

    @classmethod
    def to_json(cls) -> NoneJSON:
        return NoneJSON(
            kind="None",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "None": {},
        }


@dataclass
class Clear:
    discriminator: typing.ClassVar = 1
    kind: typing.ClassVar = "Clear"

    @classmethod
    def to_json(cls) -> ClearJSON:
        return ClearJSON(
            kind="Clear",
        )

    @classmethod
    def to_encodable(cls) -> dict:
        return {
            "Clear": {},
        }


@dataclass
class Set:
    discriminator: typing.ClassVar = 2
    kind: typing.ClassVar = "Set"
    value: SetValue

    def to_json(self) -> SetJSON:
        return SetJSON(
            kind="Set",
            value=(self.value[0].to_json(),),
        )

    def to_encodable(self) -> dict:
        return {
            "Set": {
                "item_0": self.value[0].to_encodable(),
            },
        }


UsesToggleKind = typing.Union[None_, Clear, Set]
UsesToggleJSON = typing.Union[NoneJSON, ClearJSON, SetJSON]


def from_decoded(obj: dict) -> UsesToggleKind:
    if not isinstance(obj, dict):
        raise ValueError("Invalid enum object")
    if "None" in obj:
        return None_()
    if "Clear" in obj:
        return Clear()
    if "Set" in obj:
        val = obj["Set"]
        return Set((uses.Uses.from_decoded(val["item_0"]),))
    raise ValueError("Invalid enum object")


def from_json(obj: UsesToggleJSON) -> UsesToggleKind:
    if obj["kind"] == "None":
        return None_()
    if obj["kind"] == "Clear":
        return Clear()
    if obj["kind"] == "Set":
        set_json_value = typing.cast(SetJSONValue, obj["value"])
        return Set((uses.Uses.from_json(set_json_value[0]),))
    kind = obj["kind"]
    raise ValueError(f"Unrecognized enum kind: {kind}")


layout = EnumForCodegen(
    "None" / borsh.CStruct(),
    "Clear" / borsh.CStruct(),
    "Set" / borsh.CStruct("item_0" / uses.Uses.layout),
)
