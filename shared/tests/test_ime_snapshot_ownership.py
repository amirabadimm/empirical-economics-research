"""Contracts for shared, content-addressed IME physical snapshots."""
from pathlib import Path
from tempfile import TemporaryDirectory

from shared.ime_data.ime_physical_collector import archive_market_response


def test_identical_full_market_response_is_stored_once() -> None:
    with TemporaryDirectory() as directory:
        snapshot_dir = Path(directory)
        payload = {"GregorianFromDate": "1405/05/01", "GregorianToDate": "1405/05/31"}
        first = archive_market_response(
            b'{"d":"[]"}', payload, "2026-08-29T00:00:00+00:00", 1405, 5, snapshot_dir
        )
        second = archive_market_response(
            b'{"d":"[]"}', payload, "2026-08-29T01:00:00+00:00", 1405, 5, snapshot_dir
        )
        assert first == second
        assert len(list(snapshot_dir.glob("*.json.gz"))) == 1


def test_different_source_bytes_create_distinct_immutable_snapshots() -> None:
    with TemporaryDirectory() as directory:
        snapshot_dir = Path(directory)
        payload = {"GregorianFromDate": "1405/05/01", "GregorianToDate": "1405/05/31"}
        first = archive_market_response(
            b'{"d":"[]"}', payload, "2026-08-29T00:00:00+00:00", 1405, 5, snapshot_dir
        )
        second = archive_market_response(
            b'{"d":"[1]"}', payload, "2026-08-29T01:00:00+00:00", 1405, 5, snapshot_dir
        )
        assert first != second
        assert len(list(snapshot_dir.glob("*.json.gz"))) == 2
