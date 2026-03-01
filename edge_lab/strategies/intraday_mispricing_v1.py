from collections import defaultdict

from .base import Strategy


class IntradayMispricingV1(Strategy):
    """Mispricing-focused intraday strategy (long/flat v1).

    Archetypes:
    - mean_reversion (primary)
    - jump_reaction (fade|breakout)
    """

    def __init__(
        self,
        mode: str = "mean_reversion",
        z_lookback: int = 40,
        z_entry: float = 1.5,
        z_exit: float = 0.3,
        max_hold_bars: int = 30,
        time_stop: int = 40,
        vol_lookback: int = 40,
        jump_k: float = 2.0,
        enter_mode: str = "fade",
        cooloff_after_jump: int = 3,
        max_trades_per_day: int = 10,
        min_time_between_trades_bars: int = 3,
        cooldown_bars: int = 1,
    ):
        self.mode = mode
        self.z_lookback = z_lookback
        self.z_entry = z_entry
        self.z_exit = z_exit
        self.max_hold_bars = max_hold_bars
        self.time_stop = time_stop
        self.vol_lookback = vol_lookback
        self.jump_k = jump_k
        self.enter_mode = enter_mode
        self.cooloff_after_jump = cooloff_after_jump
        self.max_trades_per_day = max_trades_per_day
        self.min_time_between_trades_bars = min_time_between_trades_bars
        self.cooldown_bars = cooldown_bars

        self._prices: list[float] = []
        self._returns: list[float] = []
        self._in_position = False
        self._hold_bars = 0
        self._cooldown_left = 0
        self._jump_cooloff_left = 0
        self._bars_since_trade = 999999
        self._day_trade_count = 0
        self._bar = 0

        self.filter_block_counts = defaultdict(int)
        self.edge_pre_cost_bps: list[float] = []
        self.edge_post_cost_bps: list[float] = []

    def _roll_mean_std(self, xs: list[float], n: int):
        if len(xs) < n:
            return 0.0, 0.0
        w = xs[-n:]
        m = sum(w) / n
        v = sum((x - m) ** 2 for x in w) / n
        return m, v ** 0.5

    def _estimate_cost_bps(self):
        # lightweight proxy for pre/post edge distribution diagnostics
        return 10.0

    def on_price(self, price: float) -> str:
        p = float(price)
        self._bar += 1

        if self._prices:
            prev = self._prices[-1]
            r = 0.0 if prev == 0 else (p - prev) / prev
            self._returns.append(r)
        self._prices.append(p)

        # pseudo day bucket for quota control (for intraday bars this approximates day boundaries)
        if self._bar % 24 == 1:
            self._day_trade_count = 0

        self._bars_since_trade += 1
        if self._cooldown_left > 0:
            self._cooldown_left -= 1
        if self._jump_cooloff_left > 0:
            self._jump_cooloff_left -= 1

        if len(self._returns) < max(self.z_lookback, self.vol_lookback):
            self.filter_block_counts["warmup"] += 1
            return "HOLD"

        r = self._returns[-1]
        mu, sd = self._roll_mean_std(self._returns, self.z_lookback)
        z = 0.0 if sd == 0 else (r - mu) / sd
        edge_bps = abs(z) * 10.0
        self.edge_pre_cost_bps.append(edge_bps)
        self.edge_post_cost_bps.append(edge_bps - self._estimate_cost_bps())

        # exit rules
        if self._in_position:
            self._hold_bars += 1
            if abs(z) <= self.z_exit or self._hold_bars >= self.max_hold_bars or self._hold_bars >= self.time_stop:
                self._in_position = False
                self._hold_bars = 0
                self._bars_since_trade = 0
                self._cooldown_left = self.cooldown_bars
                return "SELL"
            return "HOLD"

        # entry filters / quotas
        if self._day_trade_count >= self.max_trades_per_day:
            self.filter_block_counts["max_trades_per_day"] += 1
            return "HOLD"
        if self._bars_since_trade < self.min_time_between_trades_bars:
            self.filter_block_counts["min_time_between_trades"] += 1
            return "HOLD"
        if self._cooldown_left > 0:
            self.filter_block_counts["cooldown"] += 1
            return "HOLD"

        if self.mode == "mean_reversion":
            # long-only: buy on negative extreme, exit on mean-revert via z_exit rule
            if z <= -self.z_entry:
                self._in_position = True
                self._hold_bars = 0
                self._bars_since_trade = 0
                self._day_trade_count += 1
                return "BUY"
            self.filter_block_counts["z_not_extreme"] += 1
            return "HOLD"

        # jump_reaction archetype
        mu_v, sd_v = self._roll_mean_std(self._returns, self.vol_lookback)
        jump = abs(r - mu_v) > (self.jump_k * sd_v if sd_v else 0)
        if not jump:
            self.filter_block_counts["no_jump"] += 1
            return "HOLD"

        if self._jump_cooloff_left > 0:
            self.filter_block_counts["jump_cooloff"] += 1
            return "HOLD"

        should_buy = (r < 0 and self.enter_mode == "fade") or (r > 0 and self.enter_mode == "breakout")
        if should_buy:
            self._in_position = True
            self._hold_bars = 0
            self._bars_since_trade = 0
            self._day_trade_count += 1
            self._jump_cooloff_left = self.cooloff_after_jump
            return "BUY"

        self.filter_block_counts["jump_direction_filtered"] += 1
        return "HOLD"
