import json

from asset_allocation.collectors.tsetmc_fixed_income import INSTRUMENT_CODE, parse_records


def test_parse_records_orders_dates_and_marks_zero_trade_reference_row() -> None:
    payload = json.dumps({"closingPriceDaily": [
        {"dEven": 20150315, "pClosing": 10020, "pDrCotVal": 10020, "priceYesterday": 10000,
         "priceFirst": 10020, "priceMin": 10020, "priceMax": 10020, "zTotTran": 2,
         "qTotTran5J": 100, "qTotCap": 1002000},
        {"dEven": 20150314, "pClosing": 10000, "pDrCotVal": 10000, "priceYesterday": 10000,
         "priceFirst": 0, "priceMin": 0, "priceMax": 0, "zTotTran": 0,
         "qTotTran5J": 0, "qTotCap": 0},
    ]}).encode()
    records = parse_records(payload)
    assert [row["source_date_gregorian"] for row in records] == ["2015-03-14", "2015-03-15"]
    assert records[0]["has_trade"] == "false"
    assert records[1]["has_trade"] == "true"
    assert all(row["ins_code"] == INSTRUMENT_CODE for row in records)
