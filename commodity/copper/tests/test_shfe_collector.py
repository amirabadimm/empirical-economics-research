from datetime import date

from commodity.copper.src.copper.collectors.shfe import parse_payload, weekdays


def test_weekdays_excludes_weekend() -> None:
    assert weekdays(date(2026, 8, 28), date(2026, 8, 31)) == [date(2026, 8, 28), date(2026, 8, 31)]


def test_parse_payload_filters_copper_contracts() -> None:
    payload = b'{"report_date":"20260831","o_curinstrument":[{"PRODUCTID":"cu_f","DELIVERYMONTH":"2609","PRESETTLEMENTPRICE":100,"OPENPRICE":101,"HIGHESTPRICE":103,"LOWESTPRICE":99,"CLOSEPRICE":102,"SETTLEMENTPRICE":101,"ZD1_CHG":2,"ZD2_CHG":1,"VOLUME":10,"OPENINTEREST":20,"OPENINTERESTCHG":3,"TURNOVER":4.5},{"PRODUCTID":"al_f","DELIVERYMONTH":"2609"}]}'
    rows = parse_payload(payload, "url", "snapshot")
    assert len(rows) == 1
    assert rows[0]["contract"] == "cu2609"
    assert rows[0]["delivery_month"] == "2026-09"
