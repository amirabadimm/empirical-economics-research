"""Build the exact-date silver certificate/physical diagnostic."""
from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from commodity.silver.src.silver.processing.common import atomic_csv, require_columns  # noqa: E402

CERTIFICATE_REQUIRED = {"PersianDate", "DT", "TradesVolume", "TodaySettlementPrice"}
PHYSICAL_REQUIRED = {"date_jalali", "physical_price_irr_per_kg", "physical_quantity_kg",
                     "physical_product_scope", "price_method"}

def build(certificate: pd.DataFrame, physical: pd.DataFrame) -> pd.DataFrame:
    require_columns(certificate, CERTIFICATE_REQUIRED, "certificate raw")
    require_columns(physical, PHYSICAL_REQUIRED, "physical benchmark")
    cert = certificate.copy()
    cert["TradesVolume"] = pd.to_numeric(cert["TradesVolume"], errors="raise")
    cert["TodaySettlementPrice"] = pd.to_numeric(cert["TodaySettlementPrice"], errors="raise")
    cert = cert.loc[cert["TradesVolume"].gt(0) & cert["TodaySettlementPrice"].gt(0)].copy()
    if cert["PersianDate"].duplicated().any() or physical["date_jalali"].duplicated().any():
        raise ValueError("Duplicate certificate or physical dates")
    cert["date_jalali"] = cert["PersianDate"].astype(str).str.replace("-", "/", regex=False)
    cert["date"] = cert["DT"].astype(str).str[:10]
    cert["certificate_price_irr_per_gram"] = cert["TodaySettlementPrice"]
    cert["certificate_price_irr_per_kg"] = cert["TodaySettlementPrice"] * 1000
    result = cert.merge(physical, on="date_jalali", how="inner", validate="one_to_one")
    if result.empty:
        raise ValueError("No exact-date certificate/physical overlap")
    result["spread_irr_per_kg"] = result["certificate_price_irr_per_kg"] - result["physical_price_irr_per_kg"]
    result["premium_discount_pct"] = 100 * (result["certificate_price_irr_per_kg"] / result["physical_price_irr_per_kg"] - 1)
    result["certificate_unit"] = "one certificate = one gram of 999.9 silver"
    result["alignment_method"] = "exact_date_observed_cash_9999_silver_bar"
    result["comparability_status"] = "diagnostic_pending_tax_fee_and_delivery_review"
    columns = ["date", "date_jalali", "certificate_price_irr_per_gram",
               "certificate_price_irr_per_kg", "physical_price_irr_per_kg",
               "spread_irr_per_kg", "premium_discount_pct", "TradesVolume",
               "physical_quantity_kg", "certificate_unit", "alignment_method",
               "comparability_status", "physical_product_scope", "price_method"]
    return result[columns].sort_values("date").reset_index(drop=True)

def main() -> None:
    project = Path(__file__).resolve().parents[3]
    certificate = pd.read_csv(project / "data/raw/certificate/silver_certificate_raw.csv", encoding="utf-8-sig")
    physical = pd.read_csv(project / "data/processed/physical/silver_9999_cash_daily.csv", encoding="utf-8-sig")
    output = build(certificate, physical)
    atomic_csv(output, project / "data/processed/bubble/silver_certificate_physical.csv")
    print(f"silver exact-date diagnostic: {len(output)} dates")

if __name__ == "__main__":
    main()
