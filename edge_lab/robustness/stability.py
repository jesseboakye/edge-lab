def evaluate_stability_gate(
    *,
    observed_windows: int,
    observed_oos_days: int,
    trades_total: int,
    trades_per_window: list[int],
    collapse_ratio: float,
    min_windows: int = 8,
    min_oos_days: int = 120,
    min_trades_total: int = 200,
    min_trades_per_window: int = 20,
    max_collapse_ratio: float = 0.5,
) -> dict:
    failed = []

    pass_windows = observed_windows >= min_windows
    if not pass_windows:
        failed.append("INSUFFICIENT_WINDOWS")

    pass_oos = observed_oos_days >= min_oos_days
    if not pass_oos:
        failed.append("INSUFFICIENT_OOS_DAYS")

    pass_trades_total = trades_total >= min_trades_total
    if not pass_trades_total:
        failed.append("INSUFFICIENT_TRADES_TOTAL")

    pass_trades_pw = all(t >= min_trades_per_window for t in trades_per_window) if trades_per_window else False
    if not pass_trades_pw:
        failed.append("INSUFFICIENT_TRADES_PER_WINDOW")

    validity_pass = pass_windows and pass_oos and pass_trades_total and pass_trades_pw

    if not validity_pass:
        status = "INVALID"
        promotable = False
    else:
        # strict inequality required
        if collapse_ratio < max_collapse_ratio:
            status = "PASS"
            promotable = True
        else:
            status = "FAIL"
            promotable = False
            if collapse_ratio == max_collapse_ratio:
                failed.append("AT_THRESHOLD")

    return {
        "validity": {
            "min_windows": min_windows,
            "observed_windows": observed_windows,
            "min_oos_days": min_oos_days,
            "observed_oos_days": observed_oos_days,
            "min_trades_total": min_trades_total,
            "observed_trades_total": trades_total,
            "min_trades_per_window": min_trades_per_window,
            "observed_trades_per_window": trades_per_window,
            "pass": validity_pass,
            "failed_reasons": failed,
        },
        "status": status,
        "promotable": promotable,
    }
