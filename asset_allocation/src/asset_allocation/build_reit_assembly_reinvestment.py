"""Scenario: immediately reinvest approved cash at the first traded close after assembly."""

from __future__ import annotations

import csv
from pathlib import Path

import jdatetime
import pandas as pd

from asset_allocation.analyze_reit_tedpix_weekly import atomic_frame

ROOT = Path(__file__).resolve().parents[2]
RAW = ROOT / "data/raw/real_estate_funds"
LEDGER = ROOT / "config/reit_approved_distributions.csv"
OUTPUT = ROOT / "data/processed/analysis/reit_assembly_reinvested_daily.csv"
EVENTS = ROOT / "data/processed/analysis/reit_assembly_reinvestment_events.csv"
FUNDS = {
    "71945594172117613": "Arzesh Maskan",
    "45292762906823004": "Kelid",
    "67717913151786055": "Danik",
    "71595553356620707": "Kakh",
}


def reinvest_fund(prices: pd.DataFrame, events: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Compound fractional units, buying on the first traded close on/after assembly."""
    result = prices.sort_values("source_date_gregorian").reset_index(drop=True).copy()
    if result.empty or result.source_date_gregorian.duplicated().any():
        raise ValueError("Empty or duplicate traded-price history")
    if (result.traded_close_irr <= 0).any():
        raise ValueError("Nonpositive traded close")
    result["reinvested_units"] = 1.0
    records = []
    units = 1.0
    for event in events.sort_values("assembly_date_gregorian").itertuples():
        eligible = result.index[result.source_date_gregorian >= event.assembly_date_gregorian]
        if not len(eligible):
            raise ValueError(f"No traded close after assembly {event.assembly_date_gregorian}")
        ix = eligible[0]
        price = float(result.loc[ix, "traded_close_irr"])
        before = units
        units *= 1 + float(event.cash_irr_per_unit) / price
        result.loc[ix:, "reinvested_units"] = units
        records.append({"assembly_date_gregorian": event.assembly_date_gregorian,
                        "reinvestment_date_gregorian": result.loc[ix, "source_date_gregorian"],
                        "cash_irr_per_unit": event.cash_irr_per_unit,
                        "reinvestment_close_irr": price, "units_before": before,
                        "units_after": units, "evidence_status": event.evidence_status})
    result["reinvested_value_irr"] = result.reinvested_units * result.traded_close_irr
    result["reinvested_daily_return"] = result.reinvested_value_irr.pct_change()
    result["return_definition"] = "assembly_date_immediate_reinvestment_scenario_from_traded_closes"
    return result, pd.DataFrame(records)


def build() -> tuple[pd.DataFrame, pd.DataFrame]:
    ledger = pd.read_csv(LEDGER, dtype={"ins_code": str, "assembly_date_gregorian": str})
    if ledger.duplicated(["ins_code", "assembly_date_gregorian"]).any():
        raise ValueError("Duplicate approved distribution")
    if not set(ledger.ins_code).issubset(FUNDS) or (ledger.cash_irr_per_unit <= 0).any():
        raise ValueError("Unknown fund or invalid distribution")
    for event in ledger.itertuples():
        converted = jdatetime.date(*map(int, event.assembly_date_jalali.split("/"))).togregorian().isoformat()
        if converted != event.assembly_date_gregorian:
            raise ValueError("Assembly date conversion mismatch")
    panels, audits = [], []
    for code, name in FUNDS.items():
        raw = pd.read_csv(RAW / f"{code}.csv", dtype={"source_date_gregorian": str})
        raw = raw.loc[raw.has_trade.eq(True), ["source_date_gregorian", "closing_price_irr"]].copy()
        raw = raw.rename(columns={"closing_price_irr": "traded_close_irr"})
        panel, audit = reinvest_fund(raw, ledger.loc[ledger.ins_code == code])
        panel.insert(0, "ins_code", code)
        panel.insert(1, "fund", name)
        panels.append(panel)
        if not audit.empty:
            audit.insert(0, "ins_code", code)
            audit.insert(1, "fund", name)
            audits.append(audit)
    panel = pd.concat(panels, ignore_index=True)
    events = pd.concat(audits, ignore_index=True)
    atomic_frame(OUTPUT, panel)
    atomic_frame(EVENTS, events)
    return panel, events


if __name__ == "__main__":
    panel, events = build()
    print(f"Wrote {len(panel)} traded sessions and {len(events)} reinvestment events")
