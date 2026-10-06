"""Build observed-price comparisons and source-verified dividend reinvestment paths."""

from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame

ROOT = Path(__file__).resolve().parents[2]
PRICES = ROOT / "data/processed/analysis/reit_adjusted_daily.csv"
MANIFEST = ROOT / "data/raw/real_estate_funds/instruments.csv"
PAYOUTS = ROOT / "config/reit_cash_distributions.csv"
OUTPUT = ROOT / "data/processed/analysis/reit_price_adjustment_comparison.csv"
AUDIT = ROOT / "data/processed/analysis/reit_dividend_audit.csv"


def reinvest(prices: pd.DataFrame, events: pd.DataFrame) -> pd.DataFrame:
    """Buy fractional units with cash on the first traded close on/after payment."""
    result = prices.sort_values("source_date_gregorian").reset_index(drop=True).copy()
    result["reinvested_units"] = 1.0
    result["reinvested_value_irr"] = pd.NA
    units = 1.0
    for event in events.sort_values("payment_date_gregorian").itertuples():
        candidates = result.index[result.source_date_gregorian >= event.payment_date_gregorian]
        if not len(candidates):
            raise ValueError(f"No traded close on/after payment {event.payment_date_gregorian}")
        ix = candidates[0]
        price = float(result.loc[ix, "unadjusted_close_irr"])
        units *= 1 + float(event.cash_irr_per_unit) / price
        result.loc[result.index >= ix, "reinvested_units"] = units
    result["reinvested_value_irr"] = result.reinvested_units * result.unadjusted_close_irr
    return result


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    names = {str(row["ins_code"]): row["ticker"] for row in csv.DictReader(MANIFEST.open(encoding="utf-8-sig", newline=""))}
    prices = pd.read_csv(PRICES, dtype={"ins_code": str, "source_date_gregorian": str})
    events = pd.read_csv(PAYOUTS, dtype={"ins_code": str, "payment_date_gregorian": str})
    required = {"ins_code", "payment_date_gregorian", "cash_irr_per_unit", "source_url", "verification_status"}
    if not required.issubset(events.columns):
        raise ValueError(f"Payout ledger lacks {required - set(events.columns)}")
    if not events.empty:
        events.cash_irr_per_unit = pd.to_numeric(events.cash_irr_per_unit, errors="raise")
        if (events.cash_irr_per_unit <= 0).any() or events.duplicated(["ins_code", "payment_date_gregorian"]).any():
            raise ValueError("Invalid or duplicate payout")
        if not events.verification_status.eq("verified").all() or events.source_url.isna().any():
            raise ValueError("Every payout needs verified source evidence")
        if not set(events.ins_code).issubset(names):
            raise ValueError("Unknown instrument in payout ledger")
    output = []
    audit = []
    for code, group in prices.groupby("ins_code"):
        group = group.sort_values("source_date_gregorian").reset_index(drop=True).copy()
        group.insert(1, "fund", names[code])
        fund_events = events.loc[events.ins_code == code]
        if not fund_events.empty:
            group = reinvest(group, fund_events)
            group["reinvested_cumulative_return"] = group.reinvested_value_irr / group.reinvested_value_irr.iloc[0] - 1
        else:
            group["reinvested_units"] = pd.NA
            group["reinvested_value_irr"] = pd.NA
            group["reinvested_cumulative_return"] = pd.NA
        base_raw = group.unadjusted_close_irr.iloc[0]
        base_adjusted = group.adjusted_close_irr.iloc[0]
        group["unadjusted_cumulative_return"] = group.unadjusted_close_irr / base_raw - 1
        group["exchange_adjusted_cumulative_return"] = group.adjusted_close_irr / base_adjusted - 1
        output.append(group)
        audit.append({"ins_code": code, "fund": names[code], "verified_payout_count": len(fund_events),
                      "exchange_prices_differ": bool((group.adjusted_close_irr != group.unadjusted_close_irr).any()),
                      "reinvestment_status": "known_verified_payments_only_history_incomplete" if len(fund_events) else "payment_history_unverified"})
    panel = pd.concat(output, ignore_index=True)
    audit_table = pd.DataFrame(audit)
    atomic_frame(OUTPUT, panel)
    atomic_frame(AUDIT, audit_table)
    return panel, audit_table


if __name__ == "__main__":
    panel, audit = build()
    print(f"Wrote {len(panel)} daily price rows; {sum(audit.verified_payout_count)} verified payout events")
