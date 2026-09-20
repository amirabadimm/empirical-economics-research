import csv
import json

from ahrom_options.build_dataset import build, panel_row
from ahrom_options.common import RawJson, archive_json, atomic_csv, read_archive
from ahrom_options.discover_contracts import MASTER_COLUMNS, NAME_RE
from ahrom_options import optionbaaz_client
from ahrom_options.optionbaaz_client import validate_response
import pytest


CONTRACT = {"ins_code": "123", "symbol": "ضهرم1", "underlying_symbol": "اهرم",
            "underlying_ins_code": "17914401175772326", "option_type": "call",
            "strike": "100", "expiration_date": "2026-09-25"}


def test_response_identity_and_metadata_validation():
    body = {"status": "success", "data": {"symbolId": "123", "namad": "ضهرم1",
            "period": "1y", "underlyingLast": {"symbolId": "17914401175772326"},
            "optionMeta": {"strikePrice": 100, "contractType": "call"},
            "points": [], "underlyingPoints": []}}
    assert validate_response(body, CONTRACT) == []
    body["data"]["symbolId"] = "456"
    assert "symbol_id_mismatch" in validate_response(body, CONTRACT)


def test_official_arabic_yeh_name_can_be_normalized_for_discovery():
    name = "اختيارف اهرم-46000-1405/03/27".replace("ي", "ی")
    match = NAME_RE.fullmatch(name)
    assert match is not None
    assert match.groups() == ("ف", "46000", "1405/03/27")


def test_close_and_end_price_remain_distinct_and_flags_preserve_observation():
    point = {"date": "2026-09-20", "open": 1, "high": 0, "low": 0,
             "close": 1, "endPrice": 80, "volume": 0, "turnover": 0,
             "openInterest": 2, "iv": 0}
    row = panel_row(CONTRACT, point, 120)
    assert row["option_close"] == 1
    assert row["option_end_price"] == 80
    assert row["flag_iv_zero"] and row["flag_zero_volume"]
    assert row["flag_close_endprice_gap"]
    assert row["intrinsic_value"] == 20


def test_raw_archive_is_idempotent_and_detects_tampering(tmp_path):
    body = {"status": "success", "data": {"symbolId": "123"}}
    first = archive_json(tmp_path, body)
    assert archive_json(tmp_path, body) == first
    first.write_text("tampered", encoding="utf-8")
    with pytest.raises(ValueError, match="integrity mismatch"):
        archive_json(tmp_path, body)
    with pytest.raises(ValueError, match="hash mismatch"):
        read_archive(first)


def test_raw_archive_preserves_response_bytes(tmp_path):
    payload = b'{ "status" : "success", "data": {} }\n'
    path = archive_json(tmp_path, RawJson({"status": "success", "data": {}}, payload))
    assert path.read_bytes() == payload


def test_build_joins_underlying_by_exact_date_and_keeps_missing(tmp_path):
    processed = tmp_path / "data/processed"
    contract = dict(CONTRACT, status="active", expiration_jalali="1405/07/03",
                    first_available_date="2026-09-19", last_available_date="2026-09-20",
                    optionbaaz_first_date="", optionbaaz_last_date="")
    atomic_csv(processed / "ahrom_option_contracts.csv", [contract], MASTER_COLUMNS)
    response = {"status": "success", "data": {"symbolId": "123", "namad": "ضهرم1",
                "period": "1y", "underlyingLast": {"symbolId": "17914401175772326"},
                "optionMeta": {"strikePrice": 100, "contractType": "call"},
                "points": [{"date": "2026-09-19", "close": 2, "endPrice": 3},
                           {"date": "2026-09-20", "close": 4, "endPrice": 5}],
                "underlyingPoints": [{"date": "2026-09-19", "endPrice": 110}]}}
    archive = archive_json(tmp_path / "data/raw/optionbaaz/contracts/123", response)
    (processed / "download_manifest.json").write_text(
        json.dumps({"123": {"archive": str(archive.relative_to(tmp_path))}}), encoding="utf-8")
    quality = build(tmp_path)
    with (processed / "ahrom_options_history.csv").open(encoding="utf-8-sig", newline="") as source:
        rows = list(csv.DictReader(source))
    assert quality["panel_rows"] == 2
    assert rows[0]["option_close"] == "2" and rows[0]["option_end_price"] == "3"
    assert rows[1]["underlying_end_price"] == ""
    assert rows[1]["flag_missing_underlying"] == "True"


def test_collector_skips_recorded_404_until_refresh(tmp_path, monkeypatch):
    processed = tmp_path / "data/processed"
    processed.mkdir(parents=True)
    (processed / "download_audit.json").write_text(
        json.dumps({"failures": [{"ins_code": "123", "http_status": 404}]}), encoding="utf-8")
    monkeypatch.setenv("OPTIONBAAZ_ACCESS_TOKEN", "test-only")

    class NoNetwork:
        def get(self, *args, **kwargs):
            raise AssertionError("cached 404 should not trigger a request")

    monkeypatch.setattr(optionbaaz_client, "session", lambda: NoNetwork())
    result = optionbaaz_client.collect([CONTRACT], tmp_path)
    assert result["attempted"] == 0
    assert result["cached_404"] == 1
