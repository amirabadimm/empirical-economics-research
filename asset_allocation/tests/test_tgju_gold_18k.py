import json

from asset_allocation.collectors.tgju_gold_18k import parse_records


def test_parse_records_maps_tgju_ohlc_and_sorts_dates() -> None:
    payload = json.dumps({"data": [
        ["1,100", "1,000", "1,200", "1,150", "-", "-", "2013/07/23", "1392/05/01"],
        ["1,000", "900", "1,100", "1,050", "-", "-", "2013/07/22", "1392/04/31"],
    ]}).encode()
    rows = parse_records(payload, "2026-09-08T00:00:00+00:00")
    assert [row["source_date_gregorian"] for row in rows] == ["2013-07-22", "2013-07-23"]
    assert rows[0]["source_date_jalali"] == "1392-04-31"
    assert rows[0]["price_close_irr_per_gram"] == "1050.0"
