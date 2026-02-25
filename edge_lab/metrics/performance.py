def total_return(equity_curve):
    """Compute simple total return from an equity curve."""
    if not equity_curve:
        return 0.0
    start, end = equity_curve[0], equity_curve[-1]
    if start == 0:
        return 0.0
    return (end - start) / start
