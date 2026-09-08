from pathlib import Path
import json
import pytest
from options.scripts.import_capture import number, normalize, import_capture


def test_numbers_preserve_missing_zero_sign_and_units():
    assert number("۰") == "0"
    assert number("-") == ""
    assert number("-239.13") == "-239.13"
    assert number("19.277 B") == "19277000000.000"
    assert number("۱٬۲۳۴٫۵") == "1234.5"
    with pytest.raises(ValueError):
        number("not a number")


def test_missing_and_expired_values_are_not_fabricated():
    c = dict(symbol="طهرم1", option_type="put", expiry_jalali="1404/12/26",
             status="expired", strike="26,000", url=None)
    row = normalize(c, None, "test")
    assert row["iv"] == row["delta"] == ""
    assert row["detail_availability"] == "no_detail_link"
    c["url"] = "https://example.invalid/put"
    r = dict(captured_at="test", text="معاملات\nIV\n4.76\nدلتا\n-\nمدل هستون\nدلتا\n0.50")
    row = normalize(c, r, "test")
    assert row["iv"] == "4.76"
    assert row["delta"] == ""
    assert row["iv_quality"] == "expired_snapshot_not_current"
    assert row["rho"] == ""


def test_import_is_idempotent_and_checks_raw_integrity(tmp_path):
    source = tmp_path / "source"
    (source / "contracts_final").mkdir(parents=True)
    c = dict(symbol="ضهرم1", option_type="call", expiry_jalali="1405/06/25",
             status="active", strike="26000", url="https://example.invalid/call")
    r = dict(symbol=c["symbol"], captured_at="test", text="معاملات\nقیمت اعمال\n26,000\nتاریخ سررسید\n1405/06/25\nIV\n0.90\nدلتا\n0.5\nمدل هستون")
    for filename, content in {
        "inventory.json": {}, "catalog.json": {"catalog": [c]},
        "capture_complete.json": {"captured_contracts": 1},
        "contracts_final/call.json": r,
    }.items():
        (source / filename).write_text(json.dumps(content), encoding="utf-8")
    (source / "iv_history.csv").write_text("date_jalali,iv_displayed\n1404/06/16,0.63\n")
    (source / "iv_history_notes.txt").write_text("fixture")
    root = tmp_path / "project"
    first = import_capture(source, root)
    archive = Path(first["raw_directory"])
    before = {p.relative_to(archive): p.read_bytes() for p in archive.rglob("*") if p.is_file()}
    second = import_capture(source, root)
    assert first == second
    assert before == {p.relative_to(archive): p.read_bytes() for p in archive.rglob("*") if p.is_file()}
    assert first["active_with_iv"] == 1
    (archive / "catalog.json").write_text("tampered")
    with pytest.raises(ValueError, match="Existing raw archive changed"):
        import_capture(source, root)
