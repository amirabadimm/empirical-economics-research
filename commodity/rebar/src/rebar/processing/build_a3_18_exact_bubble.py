"""Build the exploratory exact-date A3/18 rebar certificate bubble."""

from __future__ import annotations

import csv
import sys
from pathlib import Path

import pandas as pd


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.rebar.src.rebar.collectors.certificate import CONFIG as CERTIFICATE_CONFIG  # noqa: E402
from commodity.rebar.src.rebar.processing.rebar_scope import (  # noqa: E402
    A3_18_PRODUCT,
    CASH_CONTRACTS,
    is_a3_18_straight_rebar,
)
from shared.ime_data.ime_physical_collector import jalali_to_gregorian, normalize_fa  # noqa: E402


PROJECT_DIR = Path(__file__).resolve().parents[3]
PHYSICAL_PATH = PROJECT_DIR / "data" / "raw" / "physical" / "rebar_physical_raw.csv"
CERTIFICATE_PATH = PROJECT_DIR / "data" / "raw" / "certificate" / "rebar_certificate_raw.csv"
OUTPUT_PATH = (
    PROJECT_DIR / "data" / "processed" / "bubble" / "rebar_a3_18_exact_date_bubble.csv"
)
OUTPUT_COLUMNS = [
    "date",
    "date_jalali",
    "physical_product_scope",
    "comparability_status",
    "physical_price_irr_per_kg",
    "physical_traded_quantity_ton",
    "physical_row_count",
    "physical_producer_count",
    "physical_producers",
    "physical_goods_names",
    "physical_symbols",
    "physical_contract_types",
    "certificate_contract_code",
    "certificate_price_irr_per_kg",
    "certificate_trades_volume_source_units",
    "certificate_trades_value_irr",
    "certificate_minus_physical_irr_per_kg",
    "certificate_vs_physical_bubble_pct",
    "alignment_method",
]


def numeric(series: pd.Series) -> pd.Series:
    return pd.to_numeric(series.astype(str).str.replace(",", "", regex=False), errors="coerce")


def gregorian_date(jalali: str) -> str:
    parts = tuple(map(int, str(jalali).replace("-", "/").split("/")[:3]))
    return "%04d-%02d-%02d" % jalali_to_gregorian(*parts)


def joined(values: pd.Series) -> str:
    return "|".join(sorted({str(value) for value in values.dropna()}))


def build_exact_bubble(
    physical_raw: pd.DataFrame,
    certificate_raw: pd.DataFrame,
    *,
    product_scope: str = A3_18_PRODUCT,
    product_predicate=is_a3_18_straight_rebar,
    comparability_status: str = "exploratory_underlying_match_pending_specification",
    alignment_method: str = "exact_date_observed_cash_a3_18",
) -> pd.DataFrame:
    """Return strict cash A3/18 bubbles on observed dates shared by both markets."""
    physical_required = {
        "GoodsName", "Symbol", "ProducerName", "ContractType", "Currency", "Unit",
        "date", "Price", "Quantity",
    }
    certificate_required = {
        "CommodityID", "ContractCode", "DT", "PersianDate", "TradesVolume", "TradesValue",
        "TodaySettlementPrice",
    }
    missing_physical = sorted(physical_required - set(physical_raw.columns))
    missing_certificate = sorted(certificate_required - set(certificate_raw.columns))
    if missing_physical or missing_certificate:
        raise ValueError(
            f"Raw schema changed; physical missing={missing_physical}; "
            f"certificate missing={missing_certificate}"
        )

    physical = physical_raw.copy()
    physical["Price"] = numeric(physical["Price"])
    physical["Quantity"] = numeric(physical["Quantity"])
    physical["contract_normalized"] = physical["ContractType"].map(normalize_fa)
    physical["currency_normalized"] = physical["Currency"].map(normalize_fa)
    physical["unit_normalized"] = physical["Unit"].map(normalize_fa)
    physical["date_jalali"] = physical["date"].astype(str).str.replace("-", "/", regex=False)
    eligible = physical.loc[
        physical["GoodsName"].map(product_predicate)
        & physical["contract_normalized"].isin(CASH_CONTRACTS)
        & physical["currency_normalized"].eq("ریال")
        & physical["unit_normalized"].eq("تن")
        & physical["Quantity"].gt(0)
        & physical["Price"].gt(0)
    ].copy()
    if eligible.empty:
        raise ValueError(f"No eligible straight {product_scope} cash physical trades were found")
    eligible["date"] = eligible["date_jalali"].map(gregorian_date)

    def aggregate(rows: pd.DataFrame) -> pd.Series:
        quantity = rows["Quantity"].sum()
        return pd.Series({
            "date_jalali": rows["date_jalali"].iloc[0],
            "physical_price_irr_per_kg": (rows["Price"] * rows["Quantity"]).sum() / quantity,
            "physical_traded_quantity_ton": quantity,
            "physical_row_count": len(rows),
            "physical_producer_count": rows["ProducerName"].nunique(),
            "physical_producers": joined(rows["ProducerName"]),
            "physical_goods_names": joined(rows["GoodsName"]),
            "physical_symbols": joined(rows["Symbol"]),
            "physical_contract_types": joined(rows["ContractType"]),
        })

    physical_daily = (
        eligible.groupby("date", sort=True)
        .apply(aggregate, include_groups=False)
        .reset_index()
    )

    certificate = certificate_raw.copy()
    for column in ("TradesVolume", "TradesValue", "TodaySettlementPrice"):
        certificate[column] = numeric(certificate[column])
    certificate["date"] = certificate["DT"].astype(str).str[:10]
    certificate = certificate.loc[
        certificate["CommodityID"].astype(str).eq(CERTIFICATE_CONFIG.commodity_id)
        & certificate["ContractCode"].astype(str).isin(CERTIFICATE_CONFIG.codes)
        & certificate["TradesVolume"].gt(0)
        & certificate["TradesValue"].gt(0)
        & certificate["TodaySettlementPrice"].gt(0)
    ].copy()
    if certificate["date"].duplicated().any():
        raise ValueError("Certificate input has duplicate positive-trade dates")
    certificate = certificate.rename(columns={
        "ContractCode": "certificate_contract_code",
        "TodaySettlementPrice": "certificate_price_irr_per_kg",
        "TradesVolume": "certificate_trades_volume_source_units",
        "TradesValue": "certificate_trades_value_irr",
    })

    output = physical_daily.merge(
        certificate[[
            "date", "certificate_contract_code", "certificate_price_irr_per_kg",
            "certificate_trades_volume_source_units", "certificate_trades_value_irr",
        ]],
        on="date",
        how="inner",
        validate="one_to_one",
    ).sort_values("date")
    if output.empty:
        raise ValueError(f"No exact-date {product_scope} physical/certificate overlaps were found")
    output["physical_product_scope"] = product_scope
    output["comparability_status"] = comparability_status
    output["certificate_minus_physical_irr_per_kg"] = (
        output["certificate_price_irr_per_kg"] - output["physical_price_irr_per_kg"]
    )
    output["certificate_vs_physical_bubble_pct"] = 100 * (
        output["certificate_price_irr_per_kg"] / output["physical_price_irr_per_kg"] - 1
    )
    output["alignment_method"] = alignment_method
    if output["date"].duplicated().any() or not output["physical_traded_quantity_ton"].gt(0).all():
        raise ValueError("Bubble output failed date or quantity validation")
    return output[OUTPUT_COLUMNS]


def write_atomic(frame: pd.DataFrame, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    frame.to_csv(temporary, index=False, encoding="utf-8-sig", quoting=csv.QUOTE_MINIMAL)
    temporary.replace(path)


def main() -> None:
    physical = pd.read_csv(PHYSICAL_PATH, encoding="utf-8-sig", low_memory=False)
    certificate = pd.read_csv(CERTIFICATE_PATH, encoding="utf-8-sig", low_memory=False)
    output = build_exact_bubble(physical, certificate)
    write_atomic(output, OUTPUT_PATH)
    print(f"Built {A3_18_PRODUCT} exact-date certificate bubble: {len(output)} observations")
    print(f"Coverage: {output.date.iloc[0]} through {output.date.iloc[-1]}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
