# edge-lab

Engineering-first ML/backtesting backbone with TDD.

## Config format
- **Default:** YAML (`.yaml` / `.yml`)
- Optional: JSON (`.json`)

## Run
Use the project virtual environment on Windows:

```powershell
.\.venv\Scripts\python.exe -m edge_lab backtest --config configs/baseline.yaml --output reports/baseline_backtest.json
.\.venv\Scripts\python.exe -m edge_lab walkforward --config configs/baseline.yaml --output reports/baseline_walkforward.json --train 10 --test 5 --step 5
```

## Tests
```powershell
.\.venv\Scripts\python.exe -m pytest -q
```
