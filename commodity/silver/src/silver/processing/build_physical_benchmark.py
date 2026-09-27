"""Build a daily IME 999.9 silver-bar cash benchmark in IRR/kg."""
from __future__ import annotations
import re
import sys
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from shared.ime_data.ime_physical_collector import normalize_fa  # noqa: E402
from commodity.silver.src.silver.processing.common import atomic_csv, require_columns  # noqa: E402

CASH_CONTRACTS = {"نقدی", "نقدی (مچینگ)"}
REQUIRED = {"GoodsName", "Symbol", "ProducerName", "ContractType", "Currency",
            "Unit", "date", "Price", "Quantity"}

def is_9999_silver_bar(value: object) -> bool:
    text = normalize_fa(value)
    return "شمش" in text and "نقره" in text and bool(
        re.search(r"(?<!\d)999(?:[./]9|9)(?!\d)", text)
    )

def build(raw: pd.DataFrame) -> pd.DataFrame:
    require_columns(raw, REQUIRED, "physical raw")
    frame = raw.copy()
    for column in ("ContractType", "Currency", "Unit"):
        frame[column + "_normalized"] = frame[column].map(normalize_fa)
    frame["Price"] = pd.to_numeric(frame["Price"], errors="raise")
    frame["Quantity"] = pd.to_numeric(frame["Quantity"], errors="raise")
    eligible = frame.loc[
        frame["GoodsName"].map(is_9999_silver_bar)
        & frame["ContractType_normalized"].isin(CASH_CONTRACTS)
        & frame["Currency_normalized"].eq("ریال")
        & frame["Unit_normalized"].isin({"کیلوگرم", "کیلو گرم"})
        & frame["Price"].gt(0) & frame["Quantity"].gt(0)
    ].copy()
    if eligible.empty:
        raise ValueError("No eligible 999.9 silver-bar cash trades in IRR/kg")
    eligible["date_jalali"] = eligible["date"].astype(str).str.replace("-", "/", regex=False)
    eligible["trade_value"] = eligible["Price"] * eligible["Quantity"]
    output = eligible.groupby("date_jalali", as_index=False).agg(
        physical_quantity_kg=("Quantity", "sum"),
        physical_trade_value_irr=("trade_value", "sum"),
        trade_rows=("Price", "size"),
        symbols=("Symbol", lambda s: "|".join(sorted(set(map(str, s))))),
        producers=("ProducerName", lambda s: "|".join(sorted(set(map(str, s))))),
    )
    output["physical_price_irr_per_kg"] = (
        output["physical_trade_value_irr"] / output["physical_quantity_kg"]
    )
    output["physical_product_scope"] = "IME 999.9 silver bar; cash and cash-matching; IRR/kg"
    output["price_method"] = "daily_quantity_weighted_executed_price"
    return output.sort_values("date_jalali").reset_index(drop=True)

def main() -> None:
    project = Path(__file__).resolve().parents[3]
    raw = pd.read_csv(project / "data/raw/physical/silver_physical_raw.csv", encoding="utf-8-sig")
    output = build(raw)
    atomic_csv(output, project / "data/processed/physical/silver_9999_cash_daily.csv")
    print(f"silver physical benchmark: {len(output)} dates")

if __name__ == "__main__":
    main()
