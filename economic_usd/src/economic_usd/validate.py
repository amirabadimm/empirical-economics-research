"""Report coverage, gaps, duplicates, and large changes without altering data."""
from .io_utils import atomic_write, read_csv
from .paths import PROCESSED


def _month_number(value: str) -> int:
    year, month = map(int, value.split("-"))
    return year * 12 + month


def validate() -> None:
    specs = [
        ("iran_liquidity.csv", "solar_hijri_period", "iran_liquidity_thousand_billion_irr", "monthly"),
        ("iran_urban_headline_cpi.csv", "solar_hijri_period", "iran_urban_headline_cpi", "monthly"),
        ("us_cpi_urban_all_items.csv", "date", "us_cpi", "monthly"),
        ("usd_free_market.csv", "date_gregorian", "usd_irr", "daily_observed_trading_dates"),
    ]
    report = []
    for filename, date_col, value_col, frequency in specs:
        rows = read_csv(PROCESSED / filename)
        keys = [r[date_col] for r in rows]
        duplicates = len(keys) - len(set(keys))
        missing_months = 0
        if frequency == "monthly":
            months = [_month_number(k[:7]) for k in keys]
            missing_months = sum(max(0, b - a - 1) for a, b in zip(months, months[1:]))
        values = [(k, float(r[value_col])) for k, r in zip(keys, rows) if r[value_col] not in ("", ".")]
        changes = []
        for (prior_date, prior), (current_date, current) in zip(values, values[1:]):
            if prior > 0:
                changes.append((abs(current / prior - 1), prior_date, current_date))
        largest = max(changes, default=(0, "", ""))
        report.append({"dataset": filename, "rows": len(rows), "start": keys[0], "end": keys[-1], "frequency": frequency, "duplicate_keys": duplicates, "missing_months": missing_months if frequency == "monthly" else "not_applicable_nontrading_dates_not_filled", "largest_absolute_period_change": f"{largest[0]:.8f}", "largest_change_from": largest[1], "largest_change_to": largest[2], "review_note": "Large changes are diagnostic flags only; source values are retained."})
    atomic_write(PROCESSED / "data_quality_report.csv", list(report[0]), report)
    for row in report:
        print(row)


if __name__ == "__main__":
    validate()
