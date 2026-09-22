from .calendars import jalali_month_end
from .io_utils import atomic_write, read_csv
from .paths import PROCESSED, RAW


def prepare() -> None:
    source = RAW / "iran_liquidity" / "monthly_liquidity_source.csv"
    rows = read_csv(source)
    seen = set()
    output = []
    for row in sorted(rows, key=lambda r: r["solar_hijri_period"]):
        period = row["solar_hijri_period"].replace("/", "-")
        if period in seen:
            raise ValueError(f"Duplicate liquidity month: {period}")
        seen.add(period)
        liquidity = float(row["liquidity_thousand_billion_rials"])
        money = float(row["money_thousand_billion_rials"])
        quasi = float(row["quasi_money_thousand_billion_rials"])
        if abs(liquidity - money - quasi) > 0.11:
            raise ValueError(f"Accounting identity failure: {period}")
        copied_source = "data/raw/iran_liquidity/source_documents/" + "/".join(row["source_file"].replace("\\", "/").split("/")[-2:])
        output.append({"solar_hijri_period": period, "gregorian_month_end": jalali_month_end(period).isoformat(), "iran_liquidity_thousand_billion_irr": row["liquidity_thousand_billion_rials"], "money_thousand_billion_irr": row["money_thousand_billion_rials"], "quasi_money_thousand_billion_irr": row["quasi_money_thousand_billion_rials"], "frequency": "monthly", "concept": "CBI total liquidity (M2): money plus quasi-money", "source": "Central Bank of Iran selected economic indicators", "source_file": copied_source, "source_sha256": row["source_sha256"], "validation_status": row["validation_status"]})
    atomic_write(PROCESSED / "iran_liquidity.csv", list(output[0]), output)
    print(f"Iran liquidity: {len(output)} rows, {output[0]['solar_hijri_period']} through {output[-1]['solar_hijri_period']}")


if __name__ == "__main__":
    prepare()
