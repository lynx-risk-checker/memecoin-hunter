from __future__ import annotations

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class AccountKey:
    pubkey: str
    signer: bool
    writable: bool


@dataclass(frozen=True)
class TokenBalanceDelta:
    owner: str
    mint: str
    account_index: int
    pre_amount: int
    post_amount: int
    decimals: int

    @property
    def raw_delta(self) -> int:
        return self.post_amount - self.pre_amount

    @property
    def ui_delta(self) -> float:
        return self.raw_delta / (10 ** self.decimals)


@dataclass(frozen=True)
class SolBalanceDelta:
    account: str
    account_index: int
    pre_lamports: int
    post_lamports: int

    @property
    def lamport_delta(self) -> int:
        return self.post_lamports - self.pre_lamports

    @property
    def sol_delta(self) -> float:
        return self.lamport_delta / 1_000_000_000


@dataclass(frozen=True)
class ParsedTransaction:
    signature: str | None
    slot: int
    block_time: int | None
    success: bool
    fee_lamports: int
    account_keys: tuple[AccountKey, ...]
    token_deltas: tuple[TokenBalanceDelta, ...]
    sol_deltas: tuple[SolBalanceDelta, ...]


def _account_keys(transaction: dict[str, Any]) -> list[AccountKey]:
    message = transaction.get("message")
    if not isinstance(message, dict):
        return []

    keys = message.get("accountKeys", [])
    if not isinstance(keys, list):
        return []

    result: list[AccountKey] = []
    for item in keys:
        if isinstance(item, str):
            result.append(AccountKey(item, False, False))
        elif isinstance(item, dict) and isinstance(item.get("pubkey"), str):
            result.append(
                AccountKey(
                    item["pubkey"],
                    bool(item.get("signer", False)),
                    bool(item.get("writable", False)),
                )
            )

    # Versioned Solana transactions can have address-table-loaded accounts.
    # getTransaction includes their SOL balance slots in pre/postBalances, so
    # they must be appended to keep account indices aligned with those arrays.
    meta = transaction.get("_meta_for_account_keys")
    if isinstance(meta, dict):
        loaded = meta.get("loadedAddresses")
        if isinstance(loaded, dict):
            writable = loaded.get("writable", [])
            readonly = loaded.get("readonly", [])
            if isinstance(writable, list):
                result.extend(
                    AccountKey(pubkey, False, True)
                    for pubkey in writable
                    if isinstance(pubkey, str)
                )
            if isinstance(readonly, list):
                result.extend(
                    AccountKey(pubkey, False, False)
                    for pubkey in readonly
                    if isinstance(pubkey, str)
                )

    return result


def _balance_amount(item: dict[str, Any]) -> tuple[int, int]:
    token_amount = item.get("uiTokenAmount")
    if not isinstance(token_amount, dict):
        raise ValueError("Token balance is missing uiTokenAmount.")
    amount = token_amount.get("amount")
    decimals = token_amount.get("decimals")
    if not isinstance(amount, str) or not amount.isdigit():
        raise ValueError("Token balance amount must be a non-negative integer string.")
    if not isinstance(decimals, int) or decimals < 0:
        raise ValueError("Token balance decimals must be a non-negative integer.")
    return int(amount), decimals


def _token_deltas(meta: dict[str, Any]) -> tuple[TokenBalanceDelta, ...]:
    pre = {int(item["accountIndex"]): item for item in (meta.get("preTokenBalances") or []) if isinstance(item, dict) and "accountIndex" in item}
    post = {int(item["accountIndex"]): item for item in (meta.get("postTokenBalances") or []) if isinstance(item, dict) and "accountIndex" in item}
    deltas: list[TokenBalanceDelta] = []
    for index in sorted(set(pre) | set(post)):
        before, after = pre.get(index), post.get(index)
        source = after or before
        if not isinstance(source, dict):
            continue
        owner, mint = source.get("owner"), source.get("mint")
        if not isinstance(owner, str) or not isinstance(mint, str):
            continue
        pre_amount, pre_decimals = _balance_amount(before) if before else (0, _balance_amount(after)[1])
        post_amount, post_decimals = _balance_amount(after) if after else (0, pre_decimals)
        if pre_decimals != post_decimals:
            raise ValueError("Token balance decimals changed within one account.")
        delta = TokenBalanceDelta(owner, mint, index, pre_amount, post_amount, pre_decimals)
        if delta.raw_delta:
            deltas.append(delta)
    return tuple(deltas)


def _sol_deltas(meta: dict[str, Any], account_keys: list[AccountKey]) -> tuple[SolBalanceDelta, ...]:
    pre, post = meta.get("preBalances"), meta.get("postBalances")
    if not isinstance(pre, list) or not isinstance(post, list):
        return ()
    if len(pre) != len(post) or len(pre) != len(account_keys):
        raise ValueError("SOL balance arrays must align with accountKeys.")
    deltas: list[SolBalanceDelta] = []
    for index, (before, after) in enumerate(zip(pre, post)):
        if not isinstance(before, int) or not isinstance(after, int):
            raise ValueError("SOL balances must be integers.")
        delta = SolBalanceDelta(account_keys[index].pubkey, index, before, after)
        if delta.lamport_delta:
            deltas.append(delta)
    return tuple(deltas)


def parse_transaction(transaction: dict[str, Any], *, signature: str | None = None) -> ParsedTransaction:
    if not isinstance(transaction, dict):
        raise ValueError("Transaction must be an object.")
    meta, tx = transaction.get("meta"), transaction.get("transaction")
    if not isinstance(meta, dict) or not isinstance(tx, dict):
        raise ValueError("Transaction must contain meta and transaction objects.")

    tx_for_keys = dict(tx)
    tx_for_keys["_meta_for_account_keys"] = meta
    account_keys = _account_keys(tx_for_keys)
    if not account_keys:
        raise ValueError("Transaction has no accountKeys.")
    slot, block_time, fee = transaction.get("slot"), transaction.get("blockTime"), meta.get("fee", 0)
    if not isinstance(slot, int) or slot < 0:
        raise ValueError("Transaction slot must be a non-negative integer.")
    if block_time is not None and not isinstance(block_time, int):
        raise ValueError("blockTime must be an integer or null.")
    if not isinstance(fee, int) or fee < 0:
        raise ValueError("Transaction fee must be a non-negative integer.")
    signatures = tx.get("signatures")
    resolved_signature = signature
    if resolved_signature is None and isinstance(signatures, list) and signatures and isinstance(signatures[0], str):
        resolved_signature = signatures[0]
    return ParsedTransaction(resolved_signature, slot, block_time, meta.get("err") is None, fee, tuple(account_keys), _token_deltas(meta), _sol_deltas(meta, account_keys))
