from .calendars import jalali_month_end
from .io_utils import atomic_write, read_csv
from .paths import PROCESSED, RAW


def prepare() -> None:
    rows = read_csv(RAW / "iran_cpi" / "urban_cpi_series_source.csv")
    candidates = [r for r in rows if r["metric"] == "price_index" and r["category_fa"] == "شاخص کل" and r["geography_fa"] == "کل کشور - خانوارهای شهری" and r["frequency"] == "monthly"]
    preferred = [r for r in candidates if r["series_scope"] == "national_headline_historical"]
    selected = preferred or candidates
    by_period = {}
    for row in selected:
        period = row["solar_hijri_period"].replace("/", "-")
        prior = by_period.get(period)
        if prior and prior["value"] != row["value"]:
            raise ValueError(f"Conflicting headline CPI values for {period}")
        by_period[period] = row
    output = []
    for period, row in sorted(by_period.items()):
        output.append({"solar_hijri_period": period, "gregorian_month_end": jalali_month_end(period).isoformat(), "iran_urban_headline_cpi": row["value"], "base_solar_hijri_year": row["base_solar_hijri_year"], "unit": "index", "frequency": "monthly", "seasonal_adjustment": "not_seasonally_adjusted", "geography": "Iran, urban households", "category": "All items headline CPI", "source": "Statistical Center of Iran", "source_file": "data/raw/iran_cpi/sci_urban_consumer_price_index_1405_04.xlsx", "source_sha256": row["source_sha256"]})
    atomic_write(PROCESSED / "iran_urban_headline_cpi.csv", list(output[0]), output)
    print(f"Iran CPI: {len(output)} rows, {output[0]['solar_hijri_period']} through {output[-1]['solar_hijri_period']}")


if __name__ == "__main__":
    prepare()
