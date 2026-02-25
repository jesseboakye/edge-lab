import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass(frozen=True)
class StrategyConfig:
    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class BacktestConfig:
    prices: list[float]
    strategy: StrategyConfig
    initial_cash: float = 1000.0
    fee_bps: float = 5.0
    slippage_bps: float = 0.0
    risk_free_rate: float = 0.0


def load_config(path: str | Path) -> BacktestConfig:
    payload = json.loads(Path(path).read_text(encoding="utf-8"))

    strategy_raw = payload.get("strategy") or {}
    strategy = StrategyConfig(
        name=strategy_raw.get("name", "moving_average"),
        params=strategy_raw.get("params", {}),
    )

    return BacktestConfig(
        prices=list(payload["prices"]),
        strategy=strategy,
        initial_cash=float(payload.get("initial_cash", 1000.0)),
        fee_bps=float(payload.get("fee_bps", 5.0)),
        slippage_bps=float(payload.get("slippage_bps", 0.0)),
        risk_free_rate=float(payload.get("risk_free_rate", 0.0)),
    )
