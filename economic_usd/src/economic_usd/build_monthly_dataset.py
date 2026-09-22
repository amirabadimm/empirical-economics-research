from collections import defaultdict

from .io_utils import atomic_write, read_csv
from .paths import PROCESSED


def build() -> None:
    liquidity = {r["solar_hijri_period"]: r for r in read_csv(PROCESSED / "iran_liquidity.csv")}
    iran_cpi = {r["solar_hijri_period"]: r for r in read_csv(PROCESSED / "iran_urban_headline_cpi.csv")}
    usd_daily = read_csv(PROCESSED / "usd_free_market.csv")
    usd_monthly = {}
    for row in usd_daily:
        period = row["date_jalali"][:7].replace("/", "-")
        usd_monthly[period] = row
    us_cpi = {r["date"][:7]: r for r in read_csv(PROCESSED / "us_cpi_urban_all_items.csv")}
    periods = sorted(set(liquidity) | set(iran_cpi) | set(usd_monthly))
    output = []
    for period in periods:
        liq, ir, fx = liquidity.get(period, {}), iran_cpi.get(period, {}), usd_monthly.get(period, {})
        greg_month = (liq.get("gregorian_month_end") or ir.get("gregorian_month_end") or fx.get("date_gregorian", ""))[:7]
        us = us_cpi.get(greg_month, {})
        output.append({"solar_hijri_period": period, "gregorian_reference_month": greg_month, "usd_irr_month_end_observation": fx.get("usd_irr", ""), "usd_observation_date_jalali": fx.get("date_jalali", ""), "iran_liquidity_thousand_billion_irr": liq.get("iran_liquidity_thousand_billion_irr", ""), "iran_urban_headline_cpi": ir.get("iran_urban_headline_cpi", ""), "us_cpi": us.get("us_cpi", ""), "alignment_note": "USD is last observed free-market date in Jalali month; CPI and liquidity retain published monthly values; US CPI matched to Gregorian month containing Iranian month-end"})
    atomic_write(PROCESSED / "macro_monthly.csv", list(output[0]), output)
    print(f"Monthly master: {len(output)} rows, {output[0]['solar_hijri_period']} through {output[-1]['solar_hijri_period']}")


if __name__ == "__main__":
    build()

