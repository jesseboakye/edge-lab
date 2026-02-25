import json

from edge_lab.cli import main


def test_cli_backtest_writes_output(tmp_path):
    cfg = tmp_path / "config.json"
    out = tmp_path / "result.json"
    cfg.write_text(
        json.dumps(
            {
                "prices": [100, 101, 102, 103],
                "strategy": {"name": "moving_average", "params": {"short_window": 2, "long_window": 3}},
                "initial_cash": 1000,
            }
        ),
        encoding="utf-8",
    )

    code = main(["backtest", "--config", str(cfg), "--output", str(out)])
    assert code == 0
    assert out.exists()

    payload = json.loads(out.read_text(encoding="utf-8"))
    assert "metrics" in payload
    assert "final_equity" in payload
