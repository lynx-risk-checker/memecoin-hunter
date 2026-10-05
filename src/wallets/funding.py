from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations

from src.data.tx_parser import ParsedTransaction


@dataclass(frozen=True)
class MoneyFlowEvidence:
    wallet: str
    source_account: str
    asset: str
    mint: str | None
    amount_raw: int
    amount_ui: float
    signature: str | None
    slot: int
    block_time: int | None
    confidence: float

    def __post_init__(self) -> None:
        if not self.wallet.strip() or not self.source_account.strip():
            raise ValueError("wallet and source_account are required")
        if self.asset not in {"SOL", "SPL"}:
            raise ValueError("asset must be SOL or SPL")
        if self.amount_raw <= 0 or self.amount_ui <= 0:
            raise ValueError("amount must be positive")
        if not 0 <= self.confidence <= 1:
            raise ValueError("confidence must be between 0 and 1")


@dataclass(frozen=True)
class FundingEvidence:
    wallet: str
    source_accounts: tuple[str, ...]
    source_count: int
    confidence: float
    money_flows: tuple[MoneyFlowEvidence, ...] = ()


def _sol_flows(wallet: str, tx: ParsedTransaction) -> list[MoneyFlowEvidence]:
    incoming = [d for d in tx.sol_deltas if d.account == wallet and d.lamport_delta > 0]
    outgoing = [d for d in tx.sol_deltas if d.account != wallet and d.lamport_delta < 0]
    if not incoming or not outgoing:
        return []

    confidence = 1.0 if len(outgoing) == 1 else 0.5
    return [
        MoneyFlowEvidence(
            wallet=wallet,
            source_account=source.account,
            asset="SOL",
            mint=None,
            amount_raw=-source.lamport_delta,
            amount_ui=-source.sol_delta,
            signature=tx.signature,
            slot=tx.slot,
            block_time=tx.block_time,
            confidence=confidence,
        )
        for source in outgoing
    ]


def _spl_flows(wallet: str, tx: ParsedTransaction) -> list[MoneyFlowEvidence]:
    incoming = [d for d in tx.token_deltas if d.owner == wallet and d.raw_delta > 0]
    outgoing = [d for d in tx.token_deltas if d.owner != wallet and d.raw_delta < 0]
    result: list[MoneyFlowEvidence] = []
    for target in incoming:
        sources = [d for d in outgoing if d.mint == target.mint]
        if not sources:
            continue
        confidence = 1.0 if len(sources) == 1 else 0.5
        for source in sources:
            result.append(
                MoneyFlowEvidence(
                    wallet=wallet,
                    source_account=source.owner,
                    asset="SPL",
                    mint=target.mint,
                    amount_raw=min(target.raw_delta, -source.raw_delta),
                    amount_ui=min(target.ui_delta, -source.ui_delta),
                    signature=tx.signature,
                    slot=tx.slot,
                    block_time=tx.block_time,
                    confidence=confidence,
                )
            )
    return result


def infer_money_flows(
    wallet: str,
    transactions: list[ParsedTransaction],
) -> tuple[MoneyFlowEvidence, ...]:
    if not wallet.strip():
        raise ValueError("wallet is required")

    result: list[MoneyFlowEvidence] = []
    for tx in transactions:
        if tx.success:
            result.extend(_sol_flows(wallet, tx))
            result.extend(_spl_flows(wallet, tx))
    return tuple(result)


def infer_funding_sources(
    wallet: str,
    transactions: list[ParsedTransaction],
    *,
    max_sources: int = 20,
) -> FundingEvidence:
    if not wallet.strip():
        raise ValueError("wallet is required")
    if max_sources <= 0:
        raise ValueError("max_sources must be positive")

    flows = infer_money_flows(wallet, transactions)
    sources = sorted({flow.source_account for flow in flows})
    ordered = tuple(sources[:max_sources])
    confidence = max(
        (flow.confidence for flow in flows if flow.source_account in ordered),
        default=0.0,
    )
    return FundingEvidence(wallet, ordered, len(ordered), confidence, flows)


@dataclass(frozen=True)
class SharedFundingEvidence:
    wallet_a: str
    wallet_b: str
    shared_sources: int
    confidence: float


def detect_shared_funding_sources(
    evidence: dict[str, FundingEvidence],
) -> tuple[SharedFundingEvidence, ...]:
    result: list[SharedFundingEvidence] = []
    for wallet_a, wallet_b in combinations(sorted(evidence), 2):
        shared = set(evidence[wallet_a].source_accounts) & set(evidence[wallet_b].source_accounts)
        if not shared:
            continue
        confidence = min(
            1.0,
            len(shared) / 3.0,
            evidence[wallet_a].confidence,
            evidence[wallet_b].confidence,
        )
        result.append(SharedFundingEvidence(wallet_a, wallet_b, len(shared), confidence))
    return tuple(result)
