import math
import statistics


def total_return(equity_curve):
    """Compute simple total return from an equity curve."""
    if not equity_curve:
        return 0.0
    start, end = equity_curve[0], equity_curve[-1]
    if start == 0:
        return 0.0
    return (end - start) / start


def max_drawdown(equity_curve):
    """Maximum drawdown as a negative fraction (e.g. -0.25)."""
    if not equity_curve:
        return 0.0

    peak = float(equity_curve[0])
    worst = 0.0
    for value in equity_curve:
        value = float(value)
        peak = max(peak, value)
        if peak > 0:
            dd = (value - peak) / peak
            worst = min(worst, dd)
    return worst


def sharpe_ratio(period_returns, risk_free_rate=0.0, periods_per_year=252):
    """Basic annualized Sharpe ratio using simple return series."""
    if not period_returns or len(period_returns) < 2:
        return 0.0

    excess = [r - risk_free_rate for r in period_returns]
    mean = statistics.mean(excess)
    std = statistics.stdev(excess)

    if std == 0:
        return 0.0

    return (mean / std) * math.sqrt(periods_per_year)
