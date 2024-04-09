from __future__ import annotations

import typing

import borsh_construct as borsh
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID

from .. import types
from ..program_id import PROGRAM_ID


class DelegateArgs(typing.TypedDict):
    delegate_args: types.delegate_args.DelegateArgsKind


layout = borsh.CStruct("delegate_args" / types.delegate_args.layout)


class DelegateAccounts(typing.TypedDict):
    delegate_record: typing.Optional[Pubkey]
    delegate: Pubkey
    metadata: Pubkey
    master_edition: typing.Optional[Pubkey]
    token_record: typing.Optional[Pubkey]
    mint: Pubkey
    token: typing.Optional[Pubkey]
    authority: Pubkey
    payer: Pubkey
    sysvar_instructions: Pubkey
    spl_token_program: typing.Optional[Pubkey]
    authorization_rules_program: typing.Optional[Pubkey]
    authorization_rules: typing.Optional[Pubkey]


def delegate(
    args: DelegateArgs,
    accounts: DelegateAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        (
            AccountMeta(
                pubkey=accounts["delegate_record"], is_signer=False, is_writable=True
            )
            if accounts["delegate_record"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        AccountMeta(pubkey=accounts["delegate"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=True),
        (
            AccountMeta(
                pubkey=accounts["master_edition"], is_signer=False, is_writable=False
            )
            if accounts["master_edition"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        (
            AccountMeta(
                pubkey=accounts["token_record"], is_signer=False, is_writable=True
            )
            if accounts["token_record"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        AccountMeta(pubkey=accounts["mint"], is_signer=False, is_writable=False),
        (
            AccountMeta(pubkey=accounts["token"], is_signer=False, is_writable=True)
            if accounts["token"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        AccountMeta(pubkey=accounts["authority"], is_signer=True, is_writable=False),
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(
            pubkey=accounts["sysvar_instructions"], is_signer=False, is_writable=False
        ),
        (
            AccountMeta(
                pubkey=accounts["spl_token_program"], is_signer=False, is_writable=False
            )
            if accounts["spl_token_program"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        (
            AccountMeta(
                pubkey=accounts["authorization_rules_program"],
                is_signer=False,
                is_writable=False,
            )
            if accounts["authorization_rules_program"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
        (
            AccountMeta(
                pubkey=accounts["authorization_rules"],
                is_signer=False,
                is_writable=False,
            )
            if accounts["authorization_rules"]
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    # TODO_ORIGINAL
    # identifier = b"Z\x93K\xb2UX\x04\x89"
    identifier = bytes([44])
    encoded_args = layout.build(
        {
            "delegate_args": args["delegate_args"].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
