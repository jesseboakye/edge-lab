import json

from edge_lab.config.schema import BacktestConfig, load_config


def test_load_config_defaults(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "prices": [100, 101, 102],
                "strategy": {"name": "moving_average", "params": {"short_window": 2, "long_window": 3}},
            }
        ),
        encoding="utf-8",
    )

    cfg = load_config(config_path)
    assert isinstance(cfg, BacktestConfig)
    assert cfg.initial_cash == 1000.0
    assert cfg.fee_bps == 5.0
    assert cfg.slippage_bps == 0.0


def test_load_config_reads_explicit_values(tmp_path):
    config_path = tmp_path / "config.json"
    config_path.write_text(
        json.dumps(
            {
                "prices": [100, 101, 102],
                "strategy": {"name": "moving_average", "params": {"short_window": 2, "long_window": 3}},
                "initial_cash": 5000,
                "fee_bps": 10,
                "slippage_bps": 2,
                "risk_free_rate": 0.0001,
            }
        ),
        encoding="utf-8",
    )

    cfg = load_config(config_path)
    assert cfg.initial_cash == 5000
    assert cfg.fee_bps == 10
    assert cfg.slippage_bps == 2
    assert cfg.risk_free_rate == 0.0001
