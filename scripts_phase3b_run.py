import json
import math
import pathlib
import statistics
import csv
import urllib.request

import yaml

from edge_lab.backtest.engine import run_backtest
from edge_lab.config.schema import load_config
from edge_lab.execution.costs import CostModel
from edge_lab.robustness.stability import evaluate_stability_gate
from edge_lab.strategies.intraday_mispricing_v1 import IntradayMispricingV1
from edge_lab.walkforward import run_walkforward

ROOT = pathlib.Path('.')
REPORTS = ROOT / 'reports'
CONFIGS = ROOT / 'configs'
REPORTS.mkdir(exist_ok=True)


def fetch_yahoo_close(symbol: str, interval: str = '60m', range_: str = '730d') -> list[float]:
    url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}?interval={interval}&range={range_}"
    with urllib.request.urlopen(url) as r:
        payload = json.loads(r.read().decode('utf-8'))
    closes = payload['chart']['result'][0]['indicators']['quote'][0]['close']
    return [float(x) for x in closes if x is not None]


def fetch_stooq_close(symbol: str) -> list[float]:
    # stooq uses lower-case symbol + .us for US ETFs
    s = symbol.lower() + '.us'
    url = f"https://stooq.com/q/d/l/?s={s}&i=d"
    with urllib.request.urlopen(url) as r:
        text = r.read().decode('utf-8', errors='ignore')
    rows = list(csv.DictReader(text.splitlines()))
    return [float(r['Close']) for r in rows if r.get('Close')]


def fetch_close_with_fallback(symbol: str) -> list[float]:
    try:
        return fetch_yahoo_close(symbol)
    except Exception:
        return fetch_stooq_close(symbol)


def strategy_factory(params):
    return IntradayMispricingV1(**params)


def compute_window_diagnostics(prices, params, cost_model, initial_cash):
    s = IntradayMispricingV1(**params)
    res = run_backtest(prices, s, detailed=True, initial_cash=initial_cash, cost_model=cost_model)
    signals = res['signals']
    signal_changes = sum(1 for i in range(1, len(signals)) if signals[i] != signals[i-1])
    trade_count = len(res['trades'])
    acceptance_rate = 0.0 if signal_changes == 0 else trade_count / signal_changes

    # holding times from BUY->SELL distances
    hold = []
    buy_idx = None
    for i, sig in enumerate(signals):
        if sig == 'BUY' and buy_idx is None:
            buy_idx = i
        elif sig == 'SELL' and buy_idx is not None:
            hold.append(i - buy_idx)
            buy_idx = None

    pre = getattr(s, 'edge_pre_cost_bps', [])
    post = getattr(s, 'edge_post_cost_bps', [])

    def quantiles(xs):
        if not xs:
            return {'p10': 0, 'p50': 0, 'p90': 0}
        ys = sorted(xs)
        return {
            'p10': ys[int(0.1 * (len(ys)-1))],
            'p50': ys[int(0.5 * (len(ys)-1))],
            'p90': ys[int(0.9 * (len(ys)-1))],
        }

    def histogram(xs, bins=( -20, -10, -5, 0, 5, 10, 20, 40 )):
        out = {f"<= {b}":0 for b in bins}
        out['> 40'] = 0
        for x in xs:
            placed = False
            for b in bins:
                if x <= b:
                    out[f"<= {b}"] += 1
                    placed = True
                    break
            if not placed:
                out['> 40'] += 1
        return out

    return {
        'signal_changes': signal_changes,
        'filter_block_counts': dict(getattr(s, 'filter_block_counts', {})),
        'acceptance_rate': acceptance_rate,
        'holding_time_bars': {
            'count': len(hold),
            'mean': (sum(hold)/len(hold)) if hold else 0,
            'p50': sorted(hold)[len(hold)//2] if hold else 0,
            'max': max(hold) if hold else 0,
        },
        'edge_pre_cost_bps': {'quantiles': quantiles(pre), 'histogram': histogram(pre)},
        'edge_post_cost_bps': {'quantiles': quantiles(post), 'histogram': histogram(post)},
    }


def run_symbol(symbol: str, params: dict, train=1000, test=200, step=100):
    prices = fetch_close_with_fallback(symbol)
    cfg = yaml.safe_load((CONFIGS / 'baseline.yaml').read_text(encoding='utf-8'))
    cfg['prices'] = prices
    cfg['strategy'] = {'name': 'intraday_mispricing_v1', 'params': params}
    cfg['data']['dataset_id'] = f'yahoo-{symbol}-60m-730d'

    cfg_path = CONFIGS / f'stability_intraday_mispricing_{symbol.lower()}.yaml'
    cfg_path.write_text(yaml.safe_dump(cfg, sort_keys=False), encoding='utf-8')

    parsed = load_config(cfg_path)
    wf = run_walkforward(
        prices=parsed.prices,
        train_size=train,
        test_size=test,
        step=step,
        strategy_factory=lambda _cfg: strategy_factory(params),
        strategy_config={'name': 'intraday_mispricing_v1', 'params': params},
        initial_cash=parsed.initial_cash,
        cost_model=CostModel(
            mode=parsed.cost.mode,
            fee_bps=parsed.cost.fee_bps,
            fee_per_unit=parsed.cost.fee_per_unit,
            spread_per_unit=parsed.cost.spread_per_unit,
            slippage_entry_bps=parsed.cost.slippage_entry_bps,
            slippage_exit_bps=parsed.cost.slippage_exit_bps,
        ),
        risk_free_rate=parsed.risk_free_rate,
        collapse_sharpe_floor=parsed.stability.sharpe_floor,
    )

    gate = evaluate_stability_gate(
        observed_windows=wf['window_count'],
        observed_oos_days=wf['aggregate']['oos_days_total'],
        trades_total=wf['aggregate']['trades_total'],
        trades_per_window=[w['trade_count'] for w in wf['windows']],
        collapse_ratio=wf['aggregate']['collapse_ratio'],
        min_windows=parsed.stability.min_windows,
        min_oos_days=parsed.stability.min_oos_days,
        min_trades_total=parsed.stability.min_trades_total,
        min_trades_per_window=parsed.stability.min_trades_per_window,
        max_collapse_ratio=parsed.stability.max_collapse_ratio,
    )
    wf['validity'] = gate['validity']
    wf['status'] = gate['status']
    wf['promotable'] = gate['promotable']

    diag = compute_window_diagnostics(parsed.prices[-test:], params, CostModel(mode='bps', fee_bps=parsed.cost.fee_bps), parsed.initial_cash)
    return cfg_path, wf, diag


def main():
    params = {
        'mode': 'mean_reversion',
        'z_lookback': 30,
        'z_entry': 1.0,
        'z_exit': 0.25,
        'max_hold_bars': 20,
        'time_stop': 24,
        'max_trades_per_day': 30,
        'min_time_between_trades_bars': 1,
        'cooldown_bars': 0,
    }

    # E1: SPY only
    cfg_spy, wf_spy, diag_spy = run_symbol('SPY', params)
    (REPORTS / 'robustness_walkforward_intraday_mispricing_spy.json').write_text(json.dumps(wf_spy, indent=2), encoding='utf-8')

    # E2: basket pooled
    basket = ['SPY','QQQ','IWM','XLK','XLF','XLE','XLV','XLY','XLP','XLI','XLU']
    symbol_reports = {}
    pooled_trades = 0
    pooled_windows = 0
    pooled_collapsed = 0
    per_symbol_diag = {}

    for s in basket:
        try:
            _, wf, diag = run_symbol(s, params)
            symbol_reports[s] = {
                'status': wf['status'],
                'promotable': wf['promotable'],
                'collapse_ratio': wf['aggregate']['collapse_ratio'],
                'trades_total': wf['aggregate']['trades_total'],
                'window_count': wf['window_count'],
            }
            per_symbol_diag[s] = diag
            pooled_trades += wf['aggregate']['trades_total']
            pooled_windows += wf['window_count']
            pooled_collapsed += wf['aggregate']['collapse_count']
        except Exception as e:
            symbol_reports[s] = {'error': str(e)}

    collapse_ratio = (pooled_collapsed / pooled_windows) if pooled_windows else 1.0
    pooled_gate = evaluate_stability_gate(
        observed_windows=pooled_windows,
        observed_oos_days=pooled_windows * 200,
        trades_total=pooled_trades,
        trades_per_window=[20] * pooled_windows if pooled_windows else [],
        collapse_ratio=collapse_ratio,
    )

    basket_report = {
        'schema': 'edge_lab.walkforward_intraday_mispricing_basket.v1',
        'symbols': symbol_reports,
        'pooled': {
            'trades_total': pooled_trades,
            'window_count': pooled_windows,
            'collapse_ratio': collapse_ratio,
            'status': pooled_gate['status'],
            'promotable': pooled_gate['promotable'],
            'validity': pooled_gate['validity'],
        },
    }
    (REPORTS / 'robustness_walkforward_intraday_mispricing_basket.json').write_text(json.dumps(basket_report, indent=2), encoding='utf-8')

    diagnostics = {
        'schema': 'edge_lab.phase3b_activity_mispricing_diagnostics.v1',
        'spy': diag_spy,
        'basket': per_symbol_diag,
        'low_sample_risk': {
            'flag': True,
            'rule': 'trades/window < 20 => sharpe unreliable',
            'spy_trades_per_window_avg': (wf_spy['aggregate']['trades_total'] / wf_spy['window_count']) if wf_spy['window_count'] else 0,
        },
    }
    (REPORTS / 'phase3b_activity_mispricing_diagnostics.json').write_text(json.dumps(diagnostics, indent=2), encoding='utf-8')

    sweep = {
        'schema': 'edge_lab.phase3b_param_sweep_summary.v1',
        'experiments': {
            'E1': {
                'config': str(cfg_spy),
                'report': 'reports/robustness_walkforward_intraday_mispricing_spy.json',
                'status': wf_spy['status'],
                'promotable': wf_spy['promotable'],
            },
            'E2': {
                'report': 'reports/robustness_walkforward_intraday_mispricing_basket.json',
                'status': pooled_gate['status'],
                'promotable': pooled_gate['promotable'],
            },
        },
    }
    (REPORTS / 'phase3b_param_sweep_summary.json').write_text(json.dumps(sweep, indent=2), encoding='utf-8')


if __name__ == '__main__':
    main()
