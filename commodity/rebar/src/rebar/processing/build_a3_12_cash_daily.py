"""Build the exploratory daily A3 / 12 mm cash-rebar comparison dataset."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.rebar.src.rebar.processing.rebar_scope import (  # noqa: E402
    A3_12_PRODUCT,
    CASH_CONTRACTS,
    is_a3_12_straight_rebar,
)
from shared.ime_data.ime_physical_collector import normalize_fa  # noqa: E402


PROJECT_DIR = Path(__file__).resolve().parents[3]
RAW_PATH = PROJECT_DIR / "data" / "raw" / "physical" / "rebar_physical_raw.csv"
OUTPUT_PATH = PROJECT_DIR / "data" / "processed" / "rebar_a3_12_cash_daily.csv"
OUTPUT_COLUMNS = [
    "trade_date_jalali", "cash_trade_price_vwap", "offer_base_price_vwap",
    "cash_vs_offer_base_pct", "traded_quantity", "row_count", "producer_count", "producers",
    "source_goods_names", "contract_types", "symbols",
]


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


def build_daily(raw: pd.DataFrame) -> pd.DataFrame:
    """Filter documented A3 / 12 mm cash trades and aggregate their daily VWAPs."""
    required = {
        "GoodsName", "Symbol", "ContractType", "date", "Price", "ArzeBasePrice", "Quantity",
        "ProducerName",
    }
    missing = sorted(required - set(raw.columns))
    if missing:
        raise ValueError(f"Raw rebar schema changed; missing columns: {missing}")

    data = raw.copy()
    for column in ("Price", "ArzeBasePrice", "Quantity"):
        data[column] = numeric(data[column])
    data["trade_date_jalali"] = data["date"].astype(str).str.replace("-", "/", regex=False)
    data["contract_type_normalized"] = data["ContractType"].map(normalize_fa)
    eligible = data.loc[
        data["GoodsName"].map(is_a3_12_straight_rebar)
        & data["contract_type_normalized"].isin(CASH_CONTRACTS)
        & data["Quantity"].gt(0)
        & data["Price"].gt(0)
        & data["ArzeBasePrice"].gt(0)
    ].copy()
    if eligible.empty:
        raise ValueError("No eligible A3 / 12 mm cash rows were found")

    def aggregate(frame: pd.DataFrame) -> pd.Series:
        quantity = frame["Quantity"].sum()
        cash_vwap = (frame["Price"] * frame["Quantity"]).sum() / quantity
        base_vwap = (frame["ArzeBasePrice"] * frame["Quantity"]).sum() / quantity
        return pd.Series({
            "cash_trade_price_vwap": cash_vwap,
            "offer_base_price_vwap": base_vwap,
            "cash_vs_offer_base_pct": (cash_vwap / base_vwap - 1) * 100,
            "traded_quantity": quantity,
            "row_count": len(frame),
            "producer_count": frame["ProducerName"].nunique(),
            "producers": "|".join(sorted({str(value) for value in frame["ProducerName"].dropna()})),
            "source_goods_names": "|".join(sorted({str(value) for value in frame["GoodsName"].dropna()})),
            "contract_types": "|".join(sorted({str(value) for value in frame["ContractType"].dropna()})),
            "symbols": "|".join(sorted({str(value) for value in frame["Symbol"].dropna()})),
        })

    daily = (
        eligible.groupby("trade_date_jalali", sort=True)
        .apply(aggregate, include_groups=False)
        .reset_index()
        .sort_values("trade_date_jalali")
    )
    if daily["trade_date_jalali"].duplicated().any() or not daily["traded_quantity"].gt(0).all():
        raise ValueError("Daily A3 / 12 mm output failed date or quantity validation")
    return daily[OUTPUT_COLUMNS]


def write_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    temporary.replace(path)


def main() -> None:
    if not RAW_PATH.exists():
        raise FileNotFoundError(f"Collect physical data first: {RAW_PATH}")
    daily = build_daily(pd.read_csv(RAW_PATH, encoding="utf-8-sig", low_memory=False))
    write_atomic(daily, OUTPUT_PATH)
    print(f"Built {A3_12_PRODUCT} daily cash output: {len(daily)} dates")
    print(f"Coverage: {daily.trade_date_jalali.iloc[0]} through {daily.trade_date_jalali.iloc[-1]}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
