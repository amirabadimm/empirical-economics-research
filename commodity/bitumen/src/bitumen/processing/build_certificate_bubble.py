"""Rebuild the provisional 60/70 cash/cash certificate comparison for Power BI."""
from __future__ import annotations

import re
from pathlib import Path

import pandas as pd


PROJECT = Path(__file__).resolve().parents[3]
PHYSICAL = PROJECT / "data/raw/physical/bitumen_physical_raw.csv"
CERTIFICATE = PROJECT / "data/raw/certificate/bitumen_certificate_raw.csv"
OUTPUT = PROJECT / "data/processed/bubble/bitumen_certificate_bubble.csv"


def normalize(value: object) -> str:
    if pd.isna(value):
        return ""
    text = str(value).replace("ي", "ی").replace("ى", "ی").replace("ك", "ک").replace("ۀ", "ه").replace("ة", "ه").replace("ـ", "")
    return re.sub(r"\s+", " ", re.sub(r"[\u200c\u200f\u202a-\u202e]", " ", text)).strip()


def is_6070(value: str) -> bool:
    text = normalize(value)
    if any(word in text for word in ("آند آلومینیوم", "امولسیون", "پلیمری")) or re.search(r"\b(?:PG|MC|RC|SC)\s*\d", text, re.I):
        return False
    compact = re.sub(r"[\s/_-]+", "", text).upper()
    match = re.search(r"(?<![A-Z])([0-9]{4,6})(?![0-9])", compact)
    return bool(match and match.group(1) == "6070")


def main() -> None:
    physical = pd.read_csv(PHYSICAL, encoding="utf-8-sig", low_memory=False)
    certificate = pd.read_csv(CERTIFICATE, encoding="utf-8-sig", low_memory=False)
    for field in ("Quantity", "Price", "TotalPrice"):
        physical[field] = pd.to_numeric(physical[field], errors="coerce")
    for field in ("TradesVolume", "TodaySettlementPrice"):
        certificate[field] = pd.to_numeric(certificate[field], errors="raise")
    physical["date_jalali"] = physical["date"].astype(str).str.replace("-", "/", regex=False)
    for field in ("GoodsName", "Symbol", "ContractType", "Tasvieh", "Currency", "Unit", "Talar"):
        physical[field + "_clean"] = physical[field].map(normalize)
    focus = physical.loc[
        physical["GoodsName_clean"].map(is_6070)
        & ~physical["GoodsName_clean"].str.contains("صادرات", na=False)
        & ~physical["Talar_clean"].str.contains("صادرات", na=False)
        & physical["Quantity"].gt(0) & physical["Price"].gt(0) & physical["TotalPrice"].gt(0)
    ].copy()
    primary = focus.groupby(["Currency_clean", "Unit_clean"])["Quantity"].sum().idxmax()
    focus = focus.loc[(focus["Currency_clean"] == primary[0]) & (focus["Unit_clean"] == primary[1])]
    certificate = certificate.sort_values("DT")
    inception = certificate.iloc[0]["PersianDate"]
    cash = focus.loc[
        focus["date_jalali"].ge(inception)
        & focus["ContractType_clean"].eq("نقدی")
        & focus["Tasvieh_clean"].eq("نقدی")
    ].copy()
    daily = cash.groupby("date_jalali", as_index=False).agg(physical_volume=("Quantity", "sum"), physical_value=("TotalPrice", "sum"))
    daily["physical_price_irr_per_kg"] = daily["physical_value"] / daily["physical_volume"]
    traded = certificate.loc[
        certificate["TradesVolume"].gt(0) & certificate["TodaySettlementPrice"].gt(0),
        ["PersianDate", "DT", "TradesVolume", "TodaySettlementPrice"],
    ].copy()
    if traded["PersianDate"].duplicated().any():
        raise ValueError("Duplicate certificate dates")
    output = daily.merge(traded, left_on="date_jalali", right_on="PersianDate", validate="one_to_one")
    if output.empty:
        raise ValueError("No exact-date cash/cash overlap")
    output["date"] = output["DT"].str[:10]
    output["commodity"] = "bitumen"
    output["comparison"] = "domestic_6070_cash_diagnostic"
    output["physical_date"] = output["date"]
    output["physical_age_days"] = 0
    output["certificate_price_irr_per_kg"] = output["TodaySettlementPrice"]
    output["spread_irr_per_kg"] = output["certificate_price_irr_per_kg"] - output["physical_price_irr_per_kg"]
    output["premium_discount_pct"] = 100 * (output["certificate_price_irr_per_kg"] / output["physical_price_irr_per_kg"] - 1)
    output["certificate_trades_volume"] = output["TradesVolume"]
    output["physical_price_method"] = "exact_date_observed_cash_vwap"
    output["comparability_status"] = "diagnostic_unverified_certificate_unit_and_specification"
    output["physical_product_scope"] = "domestic 60/70 standard cash and observed cash settlement"
    columns = ["commodity", "comparison", "date", "date_jalali", "physical_date", "physical_age_days", "certificate_price_irr_per_kg", "physical_price_irr_per_kg", "spread_irr_per_kg", "premium_discount_pct", "certificate_trades_volume", "physical_price_method", "comparability_status", "physical_product_scope"]
    output = output[columns].sort_values("date")
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".csv.tmp")
    output.to_csv(temporary, index=False, encoding="utf-8-sig")
    temporary.replace(OUTPUT)
    print(f"{len(output)} diagnostic rows: {OUTPUT}")


if __name__ == "__main__":
    main()
