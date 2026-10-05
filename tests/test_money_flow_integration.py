from src.data.tx_parser import AccountKey, ParsedTransaction, SolBalanceDelta
from src.strategy.edge import EdgeDecision, EdgeInput, assess_edge
from src.wallets.economic_links import WalletLinkEvidence
from src.wallets.funding import detect_shared_funding_sources, infer_funding_sources, infer_money_flows
from src.wallets.manipulation_adapter import assess_cluster_manipulation, build_cluster_manipulation_input
from src.wallets.synchronization import SynchronizedActivity


def tx(wallet: str, source: str, signature: str) -> ParsedTransaction:
    return ParsedTransaction(
        signature=signature,
        slot=1,
        block_time=100,
        success=True,
        fee_lamports=5000,
        account_keys=(AccountKey(wallet, True, True), AccountKey(source, True, True)),
        token_deltas=(),
        sol_deltas=(
            SolBalanceDelta(wallet, 0, 0, 1_000_000_000),
            SolBalanceDelta(source, 1, 2_000_000_000, 999_000_000),
        ),
    )


def test_money_flow_uses_explicit_sol_balance_deltas() -> None:
    flows = infer_money_flows("W", [tx("W", "S", "sig")])
    assert len(flows) == 1
    assert flows[0].source_account == "S"
    assert flows[0].asset == "SOL"
    assert flows[0].amount_raw == 1_000_000


def test_funding_source_is_not_inferred_from_account_keys_alone() -> None:
    unrelated = ParsedTransaction(
        signature="sig2",
        slot=2,
        block_time=101,
        success=True,
        fee_lamports=5000,
        account_keys=(AccountKey("W", True, True), AccountKey("PROGRAM", False, False)),
        token_deltas=(),
        sol_deltas=(),
    )
    evidence = infer_funding_sources("W", [unrelated])
    assert evidence.source_accounts == ()
    assert evidence.confidence == 0.0


def test_shared_funding_is_derived_from_explicit_flows() -> None:
    funders = [tx("A", f"FUNDER-{i}", f"sig-a-{i}") for i in range(3)]
    funders_b = [tx("B", f"FUNDER-{i}", f"sig-b-{i}") for i in range(3)]
    a = infer_funding_sources("A", funders)
    b = infer_funding_sources("B", funders_b)
    shared = detect_shared_funding_sources({"A": a, "B": b})
    assert len(shared) == 1
    assert shared[0].shared_sources == 1


def test_cluster_evidence_can_block_edge() -> None:
    cluster_input = build_cluster_manipulation_input(
        wallet_count=3,
        wallet_links=(
            WalletLinkEvidence("A", "B", 3, 1, 0.9),
            WalletLinkEvidence("A", "C", 3, 1, 0.9),
            WalletLinkEvidence("B", "C", 3, 1, 0.9),
        ),
        synchronized=(SynchronizedActivity("A", "B", 3, 3, 1.0),),
        shared_funding=(
            type("Shared", (), {"confidence": 0.95})(),
        ),
    )
    manipulation = assess_cluster_manipulation(cluster_input)
    assert manipulation.blocked is True

    edge = assess_edge(
        EdgeInput(
            expected_value=1.0,
            flow_score=2.0,
            wallet_support=1.0,
            dev_risk_score=10.0,
            liquidity_ok=True,
            manipulation_blocked=manipulation.blocked,
            narrative_score=1.0,
        )
    )
    assert edge.decision == EdgeDecision.BUY_BLOCKED
    assert "MANIPULATION_RISK" in edge.reasons

from src.data.tx_parser import TokenBalanceDelta

def test_money_flow_supports_explicit_spl_owner_deltas() -> None:
    transaction = tx("W", "S", "spl-sig")
    transaction = ParsedTransaction(
        signature=transaction.signature,
        slot=transaction.slot,
        block_time=transaction.block_time,
        success=True,
        fee_lamports=transaction.fee_lamports,
        account_keys=transaction.account_keys,
        token_deltas=(
            TokenBalanceDelta("W", "MINT", 0, 0, 500, 2),
            TokenBalanceDelta("S", "MINT", 1, 900, 400, 2),
        ),
        sol_deltas=(),
    )
    flows = infer_money_flows("W", [transaction])
    assert len(flows) == 1
    assert flows[0].asset == "SPL"
    assert flows[0].mint == "MINT"
    assert flows[0].amount_raw == 500
