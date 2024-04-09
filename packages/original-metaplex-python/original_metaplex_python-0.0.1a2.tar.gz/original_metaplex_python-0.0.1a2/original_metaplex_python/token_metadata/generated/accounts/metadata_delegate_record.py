import typing
from dataclasses import dataclass

import borsh_construct as borsh
from anchorpy.borsh_extension import BorshPubkey

# TODO_ORIGINAL:
# from anchorpy.coder.accounts import ACCOUNT_DISCRIMINATOR_SIZE
# from anchorpy.error import AccountInvalidDiscriminator
from anchorpy.utils.rpc import get_multiple_accounts
from solana.rpc.async_api import AsyncClient
from solana.rpc.commitment import Commitment
from solders.pubkey import Pubkey

from .. import types
from ..program_id import PROGRAM_ID


class MetadataDelegateRecordJSON(typing.TypedDict):
    key: types.key.KeyJSON
    bump: int
    mint: str
    delegate: str
    update_authority: str


@dataclass
class MetadataDelegateRecord:
    discriminator: typing.ClassVar = b"\xb9\x94%kwj\xf3\xec"
    layout: typing.ClassVar = borsh.CStruct(
        "key" / types.key.layout,
        "bump" / borsh.U8,
        "mint" / BorshPubkey,
        "delegate" / BorshPubkey,
        "update_authority" / BorshPubkey,
    )
    key: types.key.KeyKind
    bump: int
    mint: Pubkey
    delegate: Pubkey
    update_authority: Pubkey

    @classmethod
    async def fetch(
        cls,
        conn: AsyncClient,
        address: Pubkey,
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.Optional["MetadataDelegateRecord"]:
        resp = await conn.get_account_info(address, commitment=commitment)
        info = resp.value
        if info is None:
            return None
        if info.owner != program_id:
            raise ValueError("Account does not belong to this program")
        bytes_data = info.data
        return cls.decode(bytes_data)

    @classmethod
    async def fetch_multiple(
        cls,
        conn: AsyncClient,
        addresses: list[Pubkey],
        commitment: typing.Optional[Commitment] = None,
        program_id: Pubkey = PROGRAM_ID,
    ) -> typing.List[typing.Optional["MetadataDelegateRecord"]]:
        infos = await get_multiple_accounts(conn, addresses, commitment=commitment)
        res: typing.List[typing.Optional["MetadataDelegateRecord"]] = []
        for info in infos:
            if info is None:
                res.append(None)
                continue
            if info.account.owner != program_id:
                raise ValueError("Account does not belong to this program")
            res.append(cls.decode(info.account.data))
        return res

    @classmethod
    def decode(cls, data: bytes) -> "MetadataDelegateRecord":
        # TODO_ORIGINAL:
        # if data[:ACCOUNT_DISCRIMINATOR_SIZE] != cls.discriminator:
        #     raise AccountInvalidDiscriminator(
        #         "The discriminator for this account is invalid"
        #     )
        # dec = MetadataDelegateRecord.layout.parse(data[ACCOUNT_DISCRIMINATOR_SIZE:])
        dec = MetadataDelegateRecord.layout.parse(data)
        return cls(
            key=types.key.from_decoded(dec.key),
            bump=dec.bump,
            mint=dec.mint,
            delegate=dec.delegate,
            update_authority=dec.update_authority,
        )

    def to_json(self) -> MetadataDelegateRecordJSON:
        return {
            "key": self.key.to_json(),
            "bump": self.bump,
            "mint": str(self.mint),
            "delegate": str(self.delegate),
            "update_authority": str(self.update_authority),
        }

    @classmethod
    def from_json(cls, obj: MetadataDelegateRecordJSON) -> "MetadataDelegateRecord":
        return cls(
            key=types.key.from_json(obj["key"]),
            bump=obj["bump"],
            mint=Pubkey.from_string(obj["mint"]),
            delegate=Pubkey.from_string(obj["delegate"]),
            update_authority=Pubkey.from_string(obj["update_authority"]),
        )
