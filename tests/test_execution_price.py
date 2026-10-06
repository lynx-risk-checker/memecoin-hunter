import pytest

from src.wallets.execution_price import derive_execution_price


def test_sol_buy_price_excludes_network_fee() -> None:
    result = derive_execution_price(
        quantity_ui=1000,
        quote_delta_ui=-1.005,
        quote_mint="SOL",
        fee_lamports=5_000_000,
    )
    assert result is not None
    assert result.quote_quantity_ui == pytest.approx(1.0)
    assert result.price_quote_per_token == pytest.approx(0.001)
    assert result.network_fee_quote == pytest.approx(0.005)
    assert result.accounting_class == "BALANCE_FLOW_ACCOUNTING"


def test_quote_received_is_not_reduced_by_fee() -> None:
    result = derive_execution_price(
        quantity_ui=1000,
        quote_delta_ui=1.0,
        quote_mint="SOL",
        fee_lamports=5_000_000,
    )
    assert result is not None
    assert result.quote_quantity_ui == pytest.approx(1.0)


def test_zero_quote_flow_is_not_a_trade() -> None:
    assert derive_execution_price(
        quantity_ui=100,
        quote_delta_ui=0,
        quote_mint="SOL",
    ) is None


def test_non_positive_quantity_is_rejected() -> None:
    with pytest.raises(ValueError):
        derive_execution_price(
            quantity_ui=0,
            quote_delta_ui=-1,
            quote_mint="SOL",
        )
