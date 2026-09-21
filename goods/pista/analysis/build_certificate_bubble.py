"""Rebuild the notebook's provisional Dahan-Bast certificate comparison."""
from __future__ import annotations

from pathlib import Path

import jdatetime
import pandas as pd


ROOT = Path(__file__).resolve().parents[1]
PHYSICAL = ROOT / "data/raw/physical/Pistachio_Weekly_Prices.xlsx"
CERTIFICATE = ROOT / "data/raw/certificate/pista_certificate_raw.csv"
OUTPUT = ROOT / "data/processed/bubble/pista_certificate_bubble.csv"


def convert_date(value: str):
    try:
        return jdatetime.date(*map(int, str(value).split("/"))).togregorian()
    except (TypeError, ValueError, AttributeError):
        return None


def build() -> pd.DataFrame:
    physical = pd.read_excel(PHYSICAL, engine="openpyxl")
    required = {"Date (Jalali)", "Dahan-Bast Min Price", "Dahan-Bast Max Price"}
    if not required.issubset(physical.columns):
        raise ValueError("Expected Dahan-Bast source columns are missing")
    physical["physical_date"] = pd.to_datetime(physical["Date (Jalali)"].map(convert_date), errors="coerce").astype("datetime64[ns]")
    physical["physical_min_toman_per_kg"] = pd.to_numeric(physical["Dahan-Bast Min Price"], errors="coerce")
    physical["physical_max_toman_per_kg"] = pd.to_numeric(physical["Dahan-Bast Max Price"], errors="coerce")
    physical["physical_mid_toman_per_kg"] = (physical["physical_min_toman_per_kg"] + physical["physical_max_toman_per_kg"]) / 2
    physical = physical.dropna(subset=["physical_date", "physical_mid_toman_per_kg"])
    physical = physical.loc[(physical["physical_min_toman_per_kg"] > 0) & (physical["physical_min_toman_per_kg"] <= physical["physical_max_toman_per_kg"])].sort_values("physical_date")
    if physical["physical_date"].duplicated().any():
        raise ValueError("Duplicate usable physical dates")
    certificate = pd.read_csv(CERTIFICATE, encoding="utf-8-sig")
    required = {"DT", "PersianDate", "ContractCode", "TradesVolume", "TodaySettlementPrice"}
    if not required.issubset(certificate.columns):
        raise ValueError("Expected certificate source columns are missing")
    certificate = certificate.loc[certificate["ContractCode"].eq("PistaCL")].copy()
    certificate["certificate_date"] = pd.to_datetime(certificate["DT"].str[:10]).astype("datetime64[ns]")
    certificate["TradesVolume"] = pd.to_numeric(certificate["TradesVolume"], errors="raise")
    certificate["TodaySettlementPrice"] = pd.to_numeric(certificate["TodaySettlementPrice"], errors="raise")
    certificate = certificate.loc[(certificate["TradesVolume"] > 0) & (certificate["TodaySettlementPrice"] > 0)].sort_values("certificate_date")
    if certificate["certificate_date"].duplicated().any():
        raise ValueError("Duplicate traded certificate dates")
    quotes = physical[["physical_date", "Date (Jalali)", "physical_min_toman_per_kg", "physical_max_toman_per_kg", "physical_mid_toman_per_kg"]].rename(columns={"Date (Jalali)": "physical_date_jalali"})
    bubble = pd.merge_asof(certificate, quotes, left_on="certificate_date", right_on="physical_date", direction="backward", tolerance=pd.Timedelta(days=6)).dropna(subset=["physical_date"]).copy()
    if bubble.empty:
        raise ValueError("No traded certificate dates match a quote within six days")
    bubble["physical_age_days"] = (bubble["certificate_date"] - bubble["physical_date"]).dt.days
    bubble["physical_mid_irr_per_kg"] = bubble["physical_mid_toman_per_kg"] * 10  # unverified unit assumption
    bubble["certificate_irr_per_kg"] = bubble["TodaySettlementPrice"]
    bubble["spread_irr_per_kg"] = bubble["certificate_irr_per_kg"] - bubble["physical_mid_irr_per_kg"]
    bubble["bubble_pct"] = 100 * (bubble["certificate_irr_per_kg"] / bubble["physical_mid_irr_per_kg"] - 1)
    bubble["physical_unit_assumption"] = "toman_per_kg"
    bubble = bubble.rename(columns={"PersianDate": "certificate_date_jalali", "TradesVolume": "certificate_trades_volume"})[["certificate_date", "certificate_date_jalali", "physical_date", "physical_date_jalali", "physical_age_days", "certificate_trades_volume", "certificate_irr_per_kg", "physical_min_toman_per_kg", "physical_max_toman_per_kg", "physical_mid_toman_per_kg", "physical_mid_irr_per_kg", "spread_irr_per_kg", "bubble_pct", "physical_unit_assumption"]]
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    temporary = OUTPUT.with_suffix(".csv.tmp")
    bubble.to_csv(temporary, index=False, encoding="utf-8-sig")
    temporary.replace(OUTPUT)
    return bubble


if __name__ == "__main__":
    print(f"Pistachio comparison rows: {len(build())}")
