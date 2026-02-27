from edge_lab.execution.costs import CostModel, apply_execution_costs


def test_bps_mode_fee_on_notional():
    cm = CostModel(mode="bps", fee_bps=10)
    px, fee = apply_execution_costs(100, "BUY", 2, cm, is_entry=True)
    assert round(px, 6) == 100.0
    assert round(fee, 6) == 0.2


def test_per_unit_mode_fee():
    cm = CostModel(mode="per_unit", fee_per_unit=0.03)
    _px, fee = apply_execution_costs(100, "SELL", 5, cm, is_entry=False)
    assert round(fee, 6) == 0.15


def test_spread_and_asymmetric_slippage_affect_price():
    cm = CostModel(mode="bps", fee_bps=0, spread_per_unit=0.02, slippage_entry_bps=5, slippage_exit_bps=10)
    buy_px, _ = apply_execution_costs(1.00, "BUY", 1, cm, is_entry=True)
    sell_px, _ = apply_execution_costs(1.00, "SELL", 1, cm, is_entry=False)
    assert buy_px > 1.00
    assert sell_px < 1.00
