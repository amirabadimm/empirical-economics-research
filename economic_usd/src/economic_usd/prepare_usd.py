from datetime import date

from .io_utils import atomic_write, read_csv
from .paths import PROCESSED, RAW


def prepare() -> None:
    source = RAW / "usd_free_market" / "usd_to_rial.csv"
    if not source.exists():
        source = RAW / "usd_free_market" / "usd_to_rial_seed.csv"
    rows = read_csv(source)
    seen = set()
    output = []
    for row in sorted(rows, key=lambda r: tuple(map(int, r["date_pr"].replace("-", "/").split("/")))):
        jalali = row["date_pr"].replace("-", "/")
        if jalali in seen:
            raise ValueError(f"Duplicate USD date: {jalali}")
        seen.add(jalali)
        gy, gm, gd = map(int, row["date_gr"].replace("-", "/").split("/"))
        greg = date(gy, gm, gd).isoformat()
        value = row["price_irr"].replace(",", "")
        output.append({"date_gregorian": greg, "date_jalali": jalali, "usd_irr": value, "unit": "IRR_per_USD", "frequency": "daily_observed_trading_dates", "market": "Iran_free_market", "source": row["source"], "price_method": row["price_method"]})
    atomic_write(PROCESSED / "usd_free_market.csv", list(output[0]), output)
    print(f"USD: {len(output)} rows, {output[0]['date_jalali']} through {output[-1]['date_jalali']}")


if __name__ == "__main__":
    prepare()
