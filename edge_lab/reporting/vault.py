import json
import uuid
from datetime import datetime, timezone
from pathlib import Path


def _utc_now() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_json(path: Path, default):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))


def ensure_dev_excludes_holdout(mode: str, dev_range: list[int], holdout_range: list[int]) -> None:
    if mode != "dev":
        return
    ds, de = dev_range
    hs, he = holdout_range
    overlap = not (de <= hs or he <= ds)
    if overlap:
        raise RuntimeError("Dev mode config overlaps holdout_range; hard-excluded by policy")


def load_freeze_file(reports_dir: Path):
    a = reports_dir / "phase2_freeze.json"
    b = reports_dir / "freeze.json"
    if a.exists():
        return a, load_json(a, {})
    if b.exists():
        return b, load_json(b, {})
    return None, None


def enforce_freeze(mode: str, reports_dir: Path, *, config_hash: str, git_commit: str, dataset_id: str, holdout_range: list[int]) -> dict:
    if mode != "final":
        return {}
    path, freeze = load_freeze_file(reports_dir)
    if freeze is None:
        raise RuntimeError("Freeze file missing: expected reports/phase2_freeze.json or reports/freeze.json")

    required = ["config_hash", "git_commit", "dataset_id", "holdout_range", "created_timestamp_utc"]
    for k in required:
        if k not in freeze:
            raise RuntimeError(f"Freeze file missing field: {k}")

    if freeze["config_hash"] != config_hash:
        raise RuntimeError("Freeze config_hash mismatch")
    if freeze["git_commit"] != git_commit:
        raise RuntimeError("Freeze git_commit mismatch with HEAD")
    if freeze["dataset_id"] != dataset_id:
        raise RuntimeError("Freeze dataset_id mismatch")
    if list(freeze["holdout_range"]) != list(holdout_range):
        raise RuntimeError("Freeze holdout_range mismatch")
    return {"freeze_file": str(path)}


def append_holdout_ledger(reports_dir: Path, *, config_hash: str, git_commit: str, dataset_id: str, holdout_tag: str, holdout_range: list[int], notes: str = "") -> str:
    ledger_path = reports_dir / "holdout_ledger.json"
    ledger = load_json(ledger_path, {"entries": []})
    entries = ledger.get("entries", [])

    for e in entries:
        if e.get("holdout_tag") == holdout_tag and e.get("dataset_id") == dataset_id and e.get("config_hash") == config_hash:
            raise RuntimeError("Holdout already run for same {holdout_tag, dataset_id, config_hash}")

    run_id = str(uuid.uuid4())
    entry = {
        "run_id": run_id,
        "run_timestamp_utc": _utc_now(),
        "config_hash": config_hash,
        "git_commit": git_commit,
        "dataset_id": dataset_id,
        "holdout_tag": holdout_tag,
        "holdout_range": list(holdout_range),
        "mode": "final",
        "notes": notes,
    }
    entries.append(entry)
    ledger["entries"] = entries
    ledger_path.write_text(json.dumps(ledger, indent=2), encoding="utf-8")
    return run_id
