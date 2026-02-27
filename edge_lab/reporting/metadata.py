from datetime import datetime, timezone
import hashlib
import json


def config_hash(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def run_metadata(
    config_payload: dict,
    *,
    git_commit: str = "unknown",
    holdout_tag: str = "vaulted-holdout-v1",
    dataset_id: str = "baseline-dataset-v1",
    seeds: list[int] | None = None,
) -> dict:
    return {
        "run_timestamp_utc": datetime.now(timezone.utc).isoformat(),
        "config_hash": config_hash(config_payload),
        "git_commit": git_commit,
        "holdout_tag": holdout_tag,
        "dataset_id": dataset_id,
        "seeds": list(seeds or []),
    }
