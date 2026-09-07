from datetime import datetime


def test_cftc_compact_date_is_unambiguous() -> None:
    assert datetime.strptime("131231", "%y%m%d").date().isoformat() == "2013-12-31"
    assert datetime.strptime("260825", "%y%m%d").date().isoformat() == "2026-08-25"
