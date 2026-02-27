from edge_lab.robustness.stability import evaluate_stability_gate


def test_invalid_when_windows_below_min():
    out = evaluate_stability_gate(
        observed_windows=2,
        observed_oos_days=200,
        trades_total=500,
        trades_per_window=[50, 50],
        collapse_ratio=0.1,
        min_windows=8,
    )
    assert out["status"] == "INVALID"
    assert "INSUFFICIENT_WINDOWS" in out["validity"]["failed_reasons"]


def test_invalid_when_trades_total_below_min():
    out = evaluate_stability_gate(
        observed_windows=10,
        observed_oos_days=200,
        trades_total=100,
        trades_per_window=[20] * 10,
        collapse_ratio=0.1,
        min_trades_total=200,
    )
    assert out["status"] == "INVALID"
    assert "INSUFFICIENT_TRADES_TOTAL" in out["validity"]["failed_reasons"]


def test_invalid_when_any_window_trades_below_min():
    out = evaluate_stability_gate(
        observed_windows=10,
        observed_oos_days=200,
        trades_total=300,
        trades_per_window=[25, 19] + [25] * 8,
        collapse_ratio=0.1,
        min_trades_per_window=20,
    )
    assert out["status"] == "INVALID"
    assert "INSUFFICIENT_TRADES_PER_WINDOW" in out["validity"]["failed_reasons"]


def test_fail_when_valid_but_collapse_ratio_at_or_above_threshold():
    out = evaluate_stability_gate(
        observed_windows=10,
        observed_oos_days=200,
        trades_total=500,
        trades_per_window=[30] * 10,
        collapse_ratio=0.5,
        max_collapse_ratio=0.5,
    )
    assert out["status"] == "FAIL"
    assert "AT_THRESHOLD" in out["validity"]["failed_reasons"]


def test_pass_only_when_valid_and_collapse_ratio_strictly_below_threshold():
    out = evaluate_stability_gate(
        observed_windows=10,
        observed_oos_days=200,
        trades_total=500,
        trades_per_window=[30] * 10,
        collapse_ratio=0.49,
        max_collapse_ratio=0.5,
    )
    assert out["status"] == "PASS"
    assert out["promotable"] is True
