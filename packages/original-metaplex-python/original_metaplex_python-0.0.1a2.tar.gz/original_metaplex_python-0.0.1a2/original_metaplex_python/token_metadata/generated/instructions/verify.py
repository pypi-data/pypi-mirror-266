from __future__ import annotations

import typing

import borsh_construct as borsh
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID

from .. import types
from ..program_id import PROGRAM_ID


class VerifyArgs(typing.TypedDict):
    verification_args: types.verification_args.VerificationArgsKind


layout = borsh.CStruct("verification_args" / types.verification_args.layout)


class VerifyAccounts(typing.TypedDict):
    authority: Pubkey
    delegate_record: typing.Optional[Pubkey]
    metadata: Pubkey
    collection_mint: typing.Optional[Pubkey]
    collection_metadata: typing.Optional[Pubkey]
    collection_master_edition: typing.Optional[Pubkey]
    sysvar_instructions: Pubkey


def verify(
    args: VerifyArgs,
    accounts: VerifyAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=False),
        (
            AccountMeta(
                pubkey=accounts["delegate_record"], is_signer=False, is_writable=False
            )
            if accounts["delegate_record"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=True),
        (
            AccountMeta(
                pubkey=accounts["collection_mint"], is_signer=False, is_writable=False
            )
            if accounts["collection_mint"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        (
            AccountMeta(
                pubkey=accounts["collection_metadata"],
                is_signer=False,
                is_writable=True,
            )
            if accounts["collection_metadata"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        (
            AccountMeta(
                pubkey=accounts["collection_master_edition"],
                is_signer=False,
                is_writable=False,
            )
            if accounts["collection_master_edition"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["sysvar_instructions"], is_signer=False, is_writable=False
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts

    # DON 29-Jan-2024 - TODO_ORIGINAL The original code uses this byte string as the identifier, however it doesn't work
    # We use the below descriminator of 42 instead which is taken from the javascript SDK.
    # identifier = b"\x85\xa1\x8d0x\xc6X\x96"
    identifier = bytes([52])
    encoded_args = layout.build(
        {
            "verification_args": args["verification_args"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
