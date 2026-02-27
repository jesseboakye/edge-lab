import argparse
import json
import subprocess
from pathlib import Path

from edge_lab.backtest.engine import run_backtest
from edge_lab.config.schema import CostConfig, load_config
from edge_lab.execution.costs import CostModel
from edge_lab.metrics.performance import max_drawdown, sharpe_ratio, total_return
from edge_lab.reporting.metadata import config_hash, run_metadata
from edge_lab.reporting.vault import append_holdout_ledger, enforce_freeze, ensure_dev_excludes_holdout
from edge_lab.robustness.perturb import add_noise
from edge_lab.robustness.regimes import split_regimes
from edge_lab.strategies.moving_average import MovingAverageStrategy
from edge_lab.walkforward import run_walkforward


def _period_returns(equity_curve):
    if len(equity_curve) < 2:
        return []
    out = []
    for i in range(1, len(equity_curve)):
        prev = equity_curve[i - 1]
        cur = equity_curve[i]
        out.append(0.0 if prev == 0 else (cur - prev) / prev)
    return out


def _build_strategy(cfg):
    if cfg.name == "moving_average":
        return MovingAverageStrategy(**cfg.params)
    raise ValueError(f"Unknown strategy: {cfg.name}")


def _build_cost(c: CostConfig) -> CostModel:
    return CostModel(
        mode=c.mode,
        fee_bps=c.fee_bps,
        fee_per_unit=c.fee_per_unit,
        spread_per_unit=c.spread_per_unit,
        slippage_entry_bps=c.slippage_entry_bps,
        slippage_exit_bps=c.slippage_exit_bps,
    )


def _metrics_payload(result, risk_free_rate: float):
    returns = _period_returns(result["equity_curve"])
    return {
        "total_return": total_return(result["equity_curve"]),
        "max_drawdown": max_drawdown(result["equity_curve"]),
        "sharpe": sharpe_ratio(returns, risk_free_rate=risk_free_rate),
    }


def _git_commit() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], text=True).strip()
    except Exception:
        return "unknown"


def _cfg_payload(cfg):
    return {
        "strategy": cfg.strategy.name,
        "strategy_params": cfg.strategy.params,
        "cost_mode": cfg.cost.mode,
        "cost": {
            "fee_bps": cfg.cost.fee_bps,
            "fee_per_unit": cfg.cost.fee_per_unit,
            "spread_per_unit": cfg.cost.spread_per_unit,
            "slippage_entry_bps": cfg.cost.slippage_entry_bps,
            "slippage_exit_bps": cfg.cost.slippage_exit_bps,
        },
        "data": {
            "dev_range": cfg.data.dev_range,
            "holdout_range": cfg.data.holdout_range,
            "holdout_tag": cfg.data.holdout_tag,
            "dataset_id": cfg.data.dataset_id,
        },
        "initial_cash": cfg.initial_cash,
        "risk_free_rate": cfg.risk_free_rate,
    }


def _metadata(cfg, mode: str, ledger_id: str | None, extra: dict | None = None):
    payload = _cfg_payload(cfg)
    if extra:
        payload.update(extra)
    m = run_metadata(
        payload,
        git_commit=_git_commit(),
        holdout_tag=cfg.data.holdout_tag,
        dataset_id=cfg.data.dataset_id,
        seeds=cfg.perturb.seeds,
    )
    m["run_mode"] = mode
    m["holdout_enforced"] = mode == "final"
    m["holdout_ledger_entry_id"] = ledger_id
    return m


def _mode_guard(cfg, mode: str, reports_dir: Path, notes: str = "") -> str | None:
    ensure_dev_excludes_holdout(mode, cfg.data.dev_range, cfg.data.holdout_range)
    if mode != "final":
        return None
    cfg_hash = config_hash(_cfg_payload(cfg))
    enforce_freeze(
        mode,
        reports_dir,
        config_hash=cfg_hash,
        git_commit=_git_commit(),
        dataset_id=cfg.data.dataset_id,
        holdout_range=cfg.data.holdout_range,
    )
    return append_holdout_ledger(
        reports_dir,
        config_hash=cfg_hash,
        git_commit=_git_commit(),
        dataset_id=cfg.data.dataset_id,
        holdout_tag=cfg.data.holdout_tag,
        holdout_range=cfg.data.holdout_range,
        notes=notes,
    )


def cmd_cost_stress(config_path: str, output_path: str, mode: str) -> int:
    cfg = load_config(config_path)
    reports_dir = Path(output_path).parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    ledger_id = _mode_guard(cfg, mode, reports_dir, notes="cost-stress")

    modes = [
        CostModel(mode="bps", fee_bps=5.0),
        CostModel(mode="bps", fee_bps=10.0),
        CostModel(mode="bps", fee_bps=20.0),
        CostModel(mode="bps", fee_bps=10.0, slippage_entry_bps=5.0, slippage_exit_bps=10.0),
        CostModel(mode="per_unit", fee_per_unit=0.01),
        CostModel(mode="per_unit", fee_per_unit=0.02),
        CostModel(mode="per_unit", fee_per_unit=0.05),
    ]
    rows = []
    for cm in modes:
        strategy = _build_strategy(cfg.strategy)
        res = run_backtest(cfg.prices, strategy, detailed=True, initial_cash=cfg.initial_cash, cost_model=cm)
        rows.append(
            {
                "mode": cm.mode,
                "fee_bps": cm.fee_bps,
                "fee_per_unit": cm.fee_per_unit,
                "slippage_entry_bps": cm.slippage_entry_bps,
                "slippage_exit_bps": cm.slippage_exit_bps,
                "metrics": _metrics_payload(res, cfg.risk_free_rate),
                "final_equity": res["final_equity"],
            }
        )
    payload = {"schema": "edge_lab.cost_stress.v2", "metadata": _metadata(cfg, mode, ledger_id), "results": rows}
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def cmd_regime_split(config_path: str, output_path: str, mode: str) -> int:
    cfg = load_config(config_path)
    reports_dir = Path(output_path).parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    ledger_id = _mode_guard(cfg, mode, reports_dir, notes="regime-split")

    regimes = split_regimes(cfg.prices, q_stress=0.75, drawdown_thresh=-0.02)
    out = {}
    for name, idxs in regimes.items():
        prices = [cfg.prices[i] for i in idxs] if idxs else []
        strategy = _build_strategy(cfg.strategy)
        res = run_backtest(prices, strategy, detailed=True, initial_cash=cfg.initial_cash, cost_model=_build_cost(cfg.cost))
        out[name] = {"count": len(prices), "metrics": _metrics_payload(res, cfg.risk_free_rate), "final_equity": res["final_equity"]}
    payload = {"schema": "edge_lab.regime_split.v2", "metadata": _metadata(cfg, mode, ledger_id), "regimes": out}
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def cmd_perturbation(config_path: str, output_path: str, mode: str) -> int:
    cfg = load_config(config_path)
    reports_dir = Path(output_path).parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    ledger_id = _mode_guard(cfg, mode, reports_dir, notes="perturbation")

    rows = []
    for eps in cfg.perturb.levels:
        for seed in cfg.perturb.seeds:
            strategy = _build_strategy(cfg.strategy)
            pert_prices = add_noise(cfg.prices, eps=float(eps), seed=int(seed))
            res = run_backtest(pert_prices, strategy, detailed=True, initial_cash=cfg.initial_cash, cost_model=_build_cost(cfg.cost))
            rows.append({"eps": eps, "seed": seed, "final_equity": res["final_equity"], "metrics": _metrics_payload(res, cfg.risk_free_rate)})

    trs = [r["metrics"]["total_return"] for r in rows] or [0.0]
    m = sum(trs) / len(trs)
    var = sum((x - m) ** 2 for x in trs) / len(trs)
    fragility_index = var ** 0.5

    payload = {
        "schema": "edge_lab.perturbation.v2",
        "metadata": _metadata(cfg, mode, ledger_id),
        "runs": rows,
        "fragility": {"overall": fragility_index, "per_feature": {"price": fragility_index}},
    }
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def cmd_walkforward(config_path: str, output_path: str, train: int, test: int, step: int, mode: str) -> int:
    cfg = load_config(config_path)
    reports_dir = Path(output_path).parent
    reports_dir.mkdir(parents=True, exist_ok=True)
    ledger_id = _mode_guard(cfg, mode, reports_dir, notes="walkforward")

    payload = run_walkforward(
        prices=cfg.prices,
        train_size=train,
        test_size=test,
        step=step,
        strategy_factory=lambda _strategy_cfg: _build_strategy(cfg.strategy),
        strategy_config={"name": cfg.strategy.name, "params": cfg.strategy.params},
        initial_cash=cfg.initial_cash,
        cost_model=_build_cost(cfg.cost),
        risk_free_rate=cfg.risk_free_rate,
        collapse_sharpe_floor=cfg.stability.sharpe_floor,
    )
    payload["schema"] = "edge_lab.walkforward.v2"
    payload["metadata"] = _metadata(cfg, mode, ledger_id, {"train": train, "test": test, "step": step})
    payload["collapse_pass"] = payload["aggregate"]["collapse_ratio"] <= cfg.stability.max_collapse_ratio
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edge-lab")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ["cost-stress", "regime-split", "perturbation"]:
        p = sub.add_parser(name)
        p.add_argument("--config", required=True)
        p.add_argument("--output", required=True)
        p.add_argument("--mode", choices=["dev", "final"], default="dev")

    p_wf = sub.add_parser("walkforward")
    p_wf.add_argument("--config", required=True)
    p_wf.add_argument("--output", required=True)
    p_wf.add_argument("--train", type=int, required=True)
    p_wf.add_argument("--test", type=int, required=True)
    p_wf.add_argument("--step", type=int, required=True)
    p_wf.add_argument("--mode", choices=["dev", "final"], default="dev")

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "cost-stress":
        return cmd_cost_stress(args.config, args.output, args.mode)
    if args.command == "regime-split":
        return cmd_regime_split(args.config, args.output, args.mode)
    if args.command == "perturbation":
        return cmd_perturbation(args.config, args.output, args.mode)
    if args.command == "walkforward":
        return cmd_walkforward(args.config, args.output, args.train, args.test, args.step, args.mode)
    parser.error("Unknown command")
    return 2
