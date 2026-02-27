import argparse
import json
import subprocess
from pathlib import Path

from edge_lab.backtest.engine import run_backtest
from edge_lab.config.schema import CostConfig, load_config
from edge_lab.execution.costs import CostModel
from edge_lab.metrics.performance import max_drawdown, sharpe_ratio, total_return
from edge_lab.reporting.metadata import run_metadata
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


def cmd_backtest(config_path: str, output_path: str) -> int:
    cfg = load_config(config_path)
    strategy = _build_strategy(cfg.strategy)
    result = run_backtest(cfg.prices, strategy, detailed=True, initial_cash=cfg.initial_cash, cost_model=_build_cost(cfg.cost))
    meta = run_metadata({"config": config_path}, git_commit=_git_commit())
    payload = {
        "schema": "edge_lab.backtest.v1",
        "metadata": meta,
        "final_equity": result["final_equity"],
        "metrics": _metrics_payload(result, cfg.risk_free_rate),
        "trades": result["trades"],
        "equity_curve": result["equity_curve"],
        "cost_mode": result["cost_mode"],
    }
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def cmd_walkforward(config_path: str, output_path: str, train: int, test: int, step: int) -> int:
    cfg = load_config(config_path)
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
        collapse_sharpe_floor=0.0,
    )
    payload["schema"] = "edge_lab.walkforward.v1"
    payload["metadata"] = run_metadata({"config": config_path}, git_commit=_git_commit())
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def cmd_cost_stress(config_path: str, output_path: str) -> int:
    cfg = load_config(config_path)
    modes = [CostModel(mode="bps", fee_bps=5.0), CostModel(mode="bps", fee_bps=10.0), CostModel(mode="bps", fee_bps=20.0), CostModel(mode="per_unit", fee_per_unit=0.01), CostModel(mode="per_unit", fee_per_unit=0.02), CostModel(mode="per_unit", fee_per_unit=0.05)]
    rows = []
    for cm in modes:
        strategy = _build_strategy(cfg.strategy)
        res = run_backtest(cfg.prices, strategy, detailed=True, initial_cash=cfg.initial_cash, cost_model=cm)
        rows.append({"mode": cm.mode, "fee_bps": cm.fee_bps, "fee_per_unit": cm.fee_per_unit, "metrics": _metrics_payload(res, cfg.risk_free_rate), "final_equity": res["final_equity"]})
    payload = {"schema": "edge_lab.cost_stress.v1", "metadata": run_metadata({"config": config_path}, git_commit=_git_commit()), "results": rows}
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def cmd_regime_split(config_path: str, output_path: str) -> int:
    cfg = load_config(config_path)
    regimes = split_regimes(cfg.prices)
    out = {}
    for name, idxs in regimes.items():
        prices = [cfg.prices[i] for i in idxs] if idxs else []
        strategy = _build_strategy(cfg.strategy)
        res = run_backtest(prices, strategy, detailed=True, initial_cash=cfg.initial_cash, cost_model=_build_cost(cfg.cost))
        out[name] = {"count": len(prices), "metrics": _metrics_payload(res, cfg.risk_free_rate), "final_equity": res["final_equity"]}
    payload = {"schema": "edge_lab.regime_split.v1", "metadata": run_metadata({"config": config_path}, git_commit=_git_commit()), "regimes": out}
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def cmd_perturbation(config_path: str, output_path: str, eps: float) -> int:
    cfg = load_config(config_path)
    strategy_a = _build_strategy(cfg.strategy)
    base = run_backtest(cfg.prices, strategy_a, detailed=True, initial_cash=cfg.initial_cash, cost_model=_build_cost(cfg.cost))
    strategy_b = _build_strategy(cfg.strategy)
    pert_prices = add_noise(cfg.prices, eps=eps)
    pert = run_backtest(pert_prices, strategy_b, detailed=True, initial_cash=cfg.initial_cash, cost_model=_build_cost(cfg.cost))
    payload = {
        "schema": "edge_lab.perturbation.v1",
        "metadata": run_metadata({"config": config_path, "eps": eps}, git_commit=_git_commit()),
        "base": {"final_equity": base["final_equity"], "metrics": _metrics_payload(base, cfg.risk_free_rate)},
        "perturbed": {"final_equity": pert["final_equity"], "metrics": _metrics_payload(pert, cfg.risk_free_rate)},
    }
    Path(output_path).write_text(json.dumps(payload, indent=2), encoding="utf-8")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="edge-lab")
    sub = parser.add_subparsers(dest="command", required=True)

    for name in ["backtest", "cost-stress", "regime-split"]:
        p = sub.add_parser(name)
        p.add_argument("--config", required=True)
        p.add_argument("--output", required=True)

    p_wf = sub.add_parser("walkforward")
    p_wf.add_argument("--config", required=True)
    p_wf.add_argument("--output", required=True)
    p_wf.add_argument("--train", type=int, required=True)
    p_wf.add_argument("--test", type=int, required=True)
    p_wf.add_argument("--step", type=int, required=True)

    p_pert = sub.add_parser("perturbation")
    p_pert.add_argument("--config", required=True)
    p_pert.add_argument("--output", required=True)
    p_pert.add_argument("--eps", type=float, default=0.001)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.command == "backtest":
        return cmd_backtest(args.config, args.output)
    if args.command == "walkforward":
        return cmd_walkforward(args.config, args.output, args.train, args.test, args.step)
    if args.command == "cost-stress":
        return cmd_cost_stress(args.config, args.output)
    if args.command == "regime-split":
        return cmd_regime_split(args.config, args.output)
    if args.command == "perturbation":
        return cmd_perturbation(args.config, args.output, args.eps)
    parser.error("Unknown command")
    return 2
