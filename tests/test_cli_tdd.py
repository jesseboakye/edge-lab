import json

from edge_lab.cli import main


def test_cli_cost_stress_writes_output(tmp_path):
    cfg = tmp_path / "config.yaml"
    out = tmp_path / "result.json"
    cfg.write_text(
        """
prices: [100,101,102,103]
strategy:
  name: moving_average
  params:
    short_window: 2
    long_window: 3
initial_cash: 1000
""".strip(),
        encoding="utf-8",
    )

    code = main(["cost-stress", "--config", str(cfg), "--output", str(out)])
    assert code == 0
    payload = json.loads(out.read_text(encoding="utf-8"))
    assert payload["schema"].startswith("edge_lab.cost_stress")
    assert "metadata" in payload
