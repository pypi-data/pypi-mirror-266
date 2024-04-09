from __future__ import annotations

import typing

import borsh_construct as borsh
from solders.instruction import AccountMeta, Instruction
from solders.pubkey import Pubkey
from solders.system_program import ID as SYS_PROGRAM_ID
from solders.sysvar import RENT
from spl.token.constants import TOKEN_PROGRAM_ID

from .. import types
from ..program_id import PROGRAM_ID


class MintNewEditionFromMasterEditionViaTokenArgs(typing.TypedDict):
    mint_new_edition_from_master_edition_via_token_args: (
        types.mint_new_edition_from_master_edition_via_token_args.MintNewEditionFromMasterEditionViaTokenArgs
    )


layout = borsh.CStruct(
    "mint_new_edition_from_master_edition_via_token_args"
    / types.mint_new_edition_from_master_edition_via_token_args.MintNewEditionFromMasterEditionViaTokenArgs.layout
)


class MintNewEditionFromMasterEditionViaTokenAccounts(typing.TypedDict):
    new_metadata: Pubkey
    new_edition: Pubkey
    master_edition: Pubkey
    new_mint: Pubkey
    edition_mark_pda: Pubkey
    new_mint_authority: Pubkey
    payer: Pubkey
    token_account_owner: Pubkey
    token_account: Pubkey
    new_metadata_update_authority: Pubkey
    metadata: Pubkey


def mint_new_edition_from_master_edition_via_token(
    args: MintNewEditionFromMasterEditionViaTokenArgs,
    accounts: MintNewEditionFromMasterEditionViaTokenAccounts,
    program_id: Pubkey = PROGRAM_ID,
    remaining_accounts: typing.Optional[typing.List[AccountMeta]] = None,
) -> Instruction:
    keys: list[AccountMeta] = [
        AccountMeta(pubkey=accounts["new_metadata"], is_signer=False, is_writable=True),
        AccountMeta(pubkey=accounts["new_edition"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["master_edition"], is_signer=False, is_writable=True
        ),
        AccountMeta(pubkey=accounts["new_mint"], is_signer=False, is_writable=True),
        AccountMeta(
            pubkey=accounts["edition_mark_pda"], is_signer=False, is_writable=True
        ),
        AccountMeta(
            pubkey=accounts["new_mint_authority"], is_signer=True, is_writable=False
        ),
        AccountMeta(pubkey=accounts["payer"], is_signer=True, is_writable=True),
        AccountMeta(
            pubkey=accounts["token_account_owner"], is_signer=True, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["token_account"], is_signer=False, is_writable=False
        ),
        AccountMeta(
            pubkey=accounts["new_metadata_update_authority"],
            is_signer=False,
            is_writable=False,
        ),
        AccountMeta(pubkey=accounts["metadata"], is_signer=False, is_writable=False),
        AccountMeta(pubkey=TOKEN_PROGRAM_ID, is_signer=False, is_writable=False),
        AccountMeta(pubkey=SYS_PROGRAM_ID, is_signer=False, is_writable=False),
        (
            AccountMeta(pubkey=RENT, is_signer=False, is_writable=False)
            if RENT
            else AccountMeta(pubkey=program_id, is_signer=False, is_writable=False)
        ),
    ]
    if remaining_accounts is not None:
        keys += remaining_accounts
    identifier = b"\xfc\xda\xbf\xa8~E}v"
    encoded_args = layout.build(
        {
            "mint_new_edition_from_master_edition_via_token_args": args[
                "mint_new_edition_from_master_edition_via_token_args"
            ].to_encodable(),
        }
    )
    data = identifier + encoded_args
    return Instruction(program_id, data, keys)
