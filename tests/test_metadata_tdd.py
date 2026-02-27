from edge_lab.reporting.metadata import config_hash, run_metadata


def test_config_hash_stable():
    a = config_hash({"x": 1, "y": 2})
    b = config_hash({"y": 2, "x": 1})
    assert a == b


def test_run_metadata_has_required_fields():
    m = run_metadata({"x": 1}, git_commit="abc123")
    assert "run_timestamp_utc" in m
    assert m["git_commit"] == "abc123"
    assert "config_hash" in m
