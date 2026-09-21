"""Reproduce the notebook's exploratory, exact-date pellet comparison."""
from __future__ import annotations

import csv
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[3]
PHYSICAL = PROJECT / "data/raw/physical/pellet_physical_raw.csv"
CERTIFICATE = PROJECT / "data/raw/certificate/pellet_certificate_raw.csv"
OUTPUT = PROJECT / "data/processed/bubble/pellet_certificate_bubble.csv"
SYMBOLS = ("GOLG-PELL-00", "GHZ-PELL-00")


def build() -> pd.DataFrame:
    physical = pd.read_csv(PHYSICAL, encoding="utf-8-sig", low_memory=False)
    certificate = pd.read_csv(CERTIFICATE, encoding="utf-8-sig", low_memory=False)
    for column in ("Price", "Quantity"):
        physical[column] = pd.to_numeric(physical[column], errors="coerce")
    for column in ("TradesVolume", "TodaySettlementPrice"):
        certificate[column] = pd.to_numeric(certificate[column], errors="raise")
    physical["date_jalali"] = physical["date"].astype(str).str.replace("-", "/", regex=False)
    cash = physical.loc[
        physical["Symbol"].isin(SYMBOLS)
        & physical["ContractType"].isin(("نقدی", "نقدی (مچینگ)"))
        & physical["Tasvieh"].eq("نقدی")
        & physical["Price"].gt(0)
        & physical["Quantity"].gt(0)
    ].copy()
    cash["weighted_value"] = cash["Price"] * cash["Quantity"]
    daily = cash.groupby(["date_jalali", "Symbol"], as_index=False).agg(
        weighted_value=("weighted_value", "sum"), quantity=("Quantity", "sum")
    )
    daily["price"] = daily["weighted_value"] / daily["quantity"]
    prices = daily.pivot(index="date_jalali", columns="Symbol", values="price")
    prices = prices.reindex(columns=SYMBOLS)
    benchmark = prices.mean(axis=1, skipna=True).rename("physical_price_irr_per_kg").to_frame()
    benchmark["physical_company_count"] = prices.notna().sum(axis=1)
    benchmark["physical_price_method"] = benchmark["physical_company_count"].map(
        {1: "single_available_company", 2: "simple_mean_of_two"}
    )
    benchmark = benchmark.reset_index()
    traded = certificate.loc[
        certificate["TradesVolume"].gt(0) & certificate["TodaySettlementPrice"].gt(0),
        ["PersianDate", "DT", "TradesVolume", "TodaySettlementPrice"],
    ].copy()
    if traded["PersianDate"].duplicated().any():
        raise ValueError("Duplicate certificate PersianDate")
    output = benchmark.merge(traded, left_on="date_jalali", right_on="PersianDate", validate="one_to_one")
    if output.empty:
        raise ValueError("No exact-date pellet comparison")
    output["date"] = pd.to_datetime(output["DT"]).dt.strftime("%Y-%m-%d")
    output["certificate_price_irr_per_kg"] = output["TodaySettlementPrice"]
    output["certificate_trades_volume"] = output["TradesVolume"]
    output["spread_irr_per_kg"] = output["certificate_price_irr_per_kg"] - output["physical_price_irr_per_kg"]
    output["bubble_pct"] = 100 * (output["certificate_price_irr_per_kg"] / output["physical_price_irr_per_kg"] - 1)
    output = output[["date", "date_jalali", "certificate_price_irr_per_kg", "physical_price_irr_per_kg", "spread_irr_per_kg", "bubble_pct", "certificate_trades_volume", "physical_company_count", "physical_price_method"]].sort_values("date")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".csv.tmp")
    output.to_csv(temporary, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    temporary.replace(OUTPUT)
    return output


if __name__ == "__main__":
    print(f"Pellet comparison rows: {len(build())}")
