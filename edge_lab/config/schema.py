import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

import yaml


@dataclass(frozen=True)
class StrategyConfig:
    name: str
    params: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True)
class CostConfig:
    mode: str = "bps"
    fee_bps: float = 5.0
    fee_per_unit: float = 0.0
    spread_per_unit: float = 0.0
    slippage_entry_bps: float = 0.0
    slippage_exit_bps: float = 0.0


@dataclass(frozen=True)
class SizingConfig:
    method: str = "fractional_kelly"
    kelly_fraction: float = 0.25
    max_exposure_frac: float = 0.2


@dataclass(frozen=True)
class StabilityConfig:
    sharpe_floor: float = 0.0
    max_collapse_ratio: float = 0.5
    min_windows: int = 8
    min_oos_days: int = 120
    min_trades_total: int = 200
    min_trades_per_window: int = 20


@dataclass(frozen=True)
class PerturbConfig:
    levels: list[float] = field(default_factory=lambda: [0.0005, 0.001, 0.002])
    seeds: list[int] = field(default_factory=lambda: [11, 23, 47])


@dataclass(frozen=True)
class DataSplitConfig:
    dev_range: list[int] = field(default_factory=lambda: [0, 16])
    holdout_range: list[int] = field(default_factory=lambda: [16, 20])
    holdout_tag: str = "vaulted-holdout-v1"
    dataset_id: str = "baseline-dataset-v1"


@dataclass(frozen=True)
class BacktestConfig:
    prices: list[float]
    strategy: StrategyConfig
    initial_cash: float = 1000.0
    risk_free_rate: float = 0.0
    cost: CostConfig = field(default_factory=CostConfig)
    sizing: SizingConfig = field(default_factory=SizingConfig)
    stability: StabilityConfig = field(default_factory=StabilityConfig)
    perturb: PerturbConfig = field(default_factory=PerturbConfig)
    data: DataSplitConfig = field(default_factory=DataSplitConfig)


def _parse(path: Path) -> dict[str, Any]:
    raw = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    if suffix in {".yaml", ".yml"}:
        return yaml.safe_load(raw) or {}
    if suffix == ".json":
        return json.loads(raw)
    return yaml.safe_load(raw) or {}


def load_config(path: str | Path) -> BacktestConfig:
    path = Path(path)
    payload = _parse(path)

    strategy_raw = payload.get("strategy") or {}
    strategy = StrategyConfig(
        name=strategy_raw.get("name", "moving_average"),
        params=strategy_raw.get("params", {}),
    )

    cost_raw = payload.get("cost") or {}
    cost = CostConfig(
        mode=str(cost_raw.get("mode", "bps")),
        fee_bps=float(cost_raw.get("fee_bps", payload.get("fee_bps", 5.0))),
        fee_per_unit=float(cost_raw.get("fee_per_unit", 0.0)),
        spread_per_unit=float(cost_raw.get("spread_per_unit", 0.0)),
        slippage_entry_bps=float(cost_raw.get("slippage_entry_bps", payload.get("slippage_bps", 0.0))),
        slippage_exit_bps=float(cost_raw.get("slippage_exit_bps", payload.get("slippage_bps", 0.0))),
    )

    sizing_raw = payload.get("sizing") or {}
    sizing = SizingConfig(
        method=str(sizing_raw.get("method", "fractional_kelly")),
        kelly_fraction=float(sizing_raw.get("kelly_fraction", 0.25)),
        max_exposure_frac=float(sizing_raw.get("max_exposure_frac", 0.2)),
    )

    stability_raw = payload.get("stability") or {}
    stability = StabilityConfig(
        sharpe_floor=float(stability_raw.get("sharpe_floor", 0.0)),
        max_collapse_ratio=float(stability_raw.get("max_collapse_ratio", 0.5)),
        min_windows=int(stability_raw.get("min_windows", 8)),
        min_oos_days=int(stability_raw.get("min_oos_days", 120)),
        min_trades_total=int(stability_raw.get("min_trades_total", 200)),
        min_trades_per_window=int(stability_raw.get("min_trades_per_window", 20)),
    )

    perturb_raw = payload.get("perturb") or {}
    perturb = PerturbConfig(
        levels=list(perturb_raw.get("levels", [0.0005, 0.001, 0.002])),
        seeds=list(perturb_raw.get("seeds", [11, 23, 47])),
    )

    data_raw = payload.get("data") or {}
    data = DataSplitConfig(
        dev_range=list(data_raw.get("dev_range", [0, 16])),
        holdout_range=list(data_raw.get("holdout_range", [16, 20])),
        holdout_tag=str(data_raw.get("holdout_tag", "vaulted-holdout-v1")),
        dataset_id=str(data_raw.get("dataset_id", "baseline-dataset-v1")),
    )

    return BacktestConfig(
        prices=list(payload["prices"]),
        strategy=strategy,
        initial_cash=float(payload.get("initial_cash", 1000.0)),
        risk_free_rate=float(payload.get("risk_free_rate", 0.0)),
        cost=cost,
        sizing=sizing,
        stability=stability,
        perturb=perturb,
        data=data,
    )
