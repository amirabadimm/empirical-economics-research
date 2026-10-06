import csv
from datetime import date

from asset_allocation.analyze_reit_tedpix_weekly import friday, shift_jalali_months, weekly_closes


def test_week_ends_friday_and_uses_last_traded_close(tmp_path):
    path = tmp_path / "fund.csv"
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=("source_date_gregorian", "closing_price_irr", "has_trade"))
        writer.writeheader()
        writer.writerows([
            {"source_date_gregorian": "2026-09-26", "closing_price_irr": "100", "has_trade": "true"},
            {"source_date_gregorian": "2026-09-29", "closing_price_irr": "105", "has_trade": "true"},
            {"source_date_gregorian": "2026-09-30", "closing_price_irr": "106", "has_trade": "false"},
            {"source_date_gregorian": "2026-10-04", "closing_price_irr": "110", "has_trade": "true"},
        ])
    closes = weekly_closes(path, "closing_price_irr", date(2026, 9, 25), date(2026, 10, 2), True)
    assert friday(date(2026, 9, 26)) == date(2026, 10, 2)
    assert list(closes) == [date(2026, 10, 2)]
    assert closes[date(2026, 10, 2)]["closing_price_irr"] == "105"


def test_jalali_month_shift_is_calendar_based():
    anchor = date(2026, 10, 2)
    assert shift_jalali_months(anchor, 24) == date(2024, 10, 1)
