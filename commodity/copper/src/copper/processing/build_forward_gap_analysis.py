"""Build the NCI forward-trade analysis for the 102-day cash benchmark gap."""

from __future__ import annotations

import csv
import gzip
import json
import sys
from collections import defaultdict
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.ime_data.ime_physical_collector import jalali_to_gregorian, normalize_fa  # noqa: E402


GAP_LEFT = "1404/09/26"
GAP_RIGHT = "1405/01/09"
TARGET_SYMBOL = "NCI-OACCAA-00"
TARGET_CONTRACTS = {"سلف", "سلف (مچینگ)"}
OUTPUT_COLUMNS = [
    "trade_date_jalali", "trade_date_gregorian", "symbols", "contract_types",
    "settlement_types", "offer_ids", "forward_rows", "forward_quantity",
    "forward_matching_quantity", "total_quantity", "forward_matching_share",
    "forward_weighted_price", "previous_cash_date_jalali", "previous_cash_price",
    "next_cash_date_jalali", "next_cash_price", "days_after_previous_cash",
    "days_before_next_cash", "gap_progress", "linear_cash_bridge_price",
    "vs_previous_cash_irr_per_kg", "vs_previous_cash_pct",
    "vs_next_cash_irr_per_kg", "vs_next_cash_pct",
    "vs_linear_bridge_irr_per_kg", "vs_linear_bridge_pct",
]


def number(value: object, field: str) -> Decimal:
    try:
        result = Decimal(str(value or "0").replace(",", "").strip())
    except InvalidOperation as exc:
        raise ValueError(f"invalid {field}: {value!r}") from exc
    if result < 0:
        raise ValueError(f"negative {field}: {result}")
    return result


def display(value: Decimal) -> str:
    if value == value.to_integral_value():
        return str(int(value))
    return format(value.normalize(), "f")


def gregorian(jalali: str) -> date:
    jy, jm, jd = map(int, jalali.replace("-", "/").split("/"))
    return date(*jalali_to_gregorian(jy, jm, jd))


def newest_valid_months(snapshot_dir: Path, months: set[str]) -> list[dict]:
    candidates: dict[str, list[Path]] = defaultdict(list)
    for path in sorted(snapshot_dir.glob("physical_*.json.gz"), reverse=True):
        month = path.name.split("_")[1]
        if month in months:
            candidates[month].append(path)
    rows: list[dict] = []
    for month in sorted(months):
        for path in candidates[month]:
            try:
                with gzip.open(path, "rt", encoding="utf-8") as handle:
                    archive = json.load(handle)
                outer = json.loads(archive["response_utf8"])
                month_rows = json.loads(outer["d"])
                if not isinstance(month_rows, list):
                    raise ValueError("snapshot rows are not a list")
                rows.extend(month_rows)
                break
            except (OSError, json.JSONDecodeError, KeyError, TypeError, ValueError):
                continue
        else:
            raise ValueError(f"no valid physical snapshot for {month}")
    return rows


def build(project: Path) -> list[dict[str, str]]:
    benchmark_path = project / "data/processed/nci_copper_cash_daily.csv"
    with benchmark_path.open("r", encoding="utf-8-sig", newline="") as handle:
        benchmark = {row["physical_trade_date_jalali"]: row for row in csv.DictReader(handle)}
    left = benchmark[GAP_LEFT]
    right = benchmark[GAP_RIGHT]
    left_price = number(left["physical_weighted_price"], "previous cash price")
    right_price = number(right["physical_weighted_price"], "next cash price")
    left_date, right_date = gregorian(GAP_LEFT), gregorian(GAP_RIGHT)
    total_gap_days = Decimal((right_date - left_date).days)
    if total_gap_days != Decimal(102):
        raise ValueError(f"expected a 102-day anchor gap, found {total_gap_days}")

    months = {"1404-09", "1404-10", "1404-11", "1404-12", "1405-01"}
    source = newest_valid_months(project / "data/raw/physical/api_snapshots", months)
    grouped: dict[str, list[dict]] = defaultdict(list)
    for row in source:
        trade_date = str(row.get("date") or "").replace("-", "/")
        if not GAP_LEFT < trade_date < GAP_RIGHT:
            continue
        if normalize_fa(row.get("GoodsName")) != "مس کاتد":
            continue
        if str(row.get("Symbol") or "").strip() != TARGET_SYMBOL:
            continue
        if normalize_fa(row.get("ProducerName")) != "ملی صنایع مس ایران":
            continue
        if normalize_fa(row.get("ContractType")) not in TARGET_CONTRACTS:
            continue
        quantity = number(row.get("Quantity"), "Quantity")
        price = number(row.get("Price"), "Price")
        if quantity > 0 and price > 0:
            grouped[trade_date].append(row)

    output: list[dict[str, str]] = []
    for trade_date in sorted(grouped):
        rows = grouped[trade_date]
        total_quantity = sum((number(row["Quantity"], "Quantity") for row in rows), Decimal(0))
        matching_quantity = sum((number(row["Quantity"], "Quantity") for row in rows
                                 if normalize_fa(row["ContractType"]) == "سلف (مچینگ)"), Decimal(0))
        weighted = sum((number(row["Price"], "Price") * number(row["Quantity"], "Quantity")
                        for row in rows), Decimal(0)) / total_quantity
        current_date = gregorian(trade_date)
        after = Decimal((current_date - left_date).days)
        before = Decimal((right_date - current_date).days)
        progress = after / total_gap_days
        bridge = left_price + progress * (right_price - left_price)
        output.append({
            "trade_date_jalali": trade_date,
            "trade_date_gregorian": current_date.isoformat(),
            "symbols": "|".join(sorted({str(row["Symbol"]) for row in rows})),
            "contract_types": "|".join(sorted({normalize_fa(row["ContractType"]) for row in rows})),
            "settlement_types": "|".join(sorted({normalize_fa(row["Tasvieh"]) for row in rows})),
            "offer_ids": "|".join(sorted({str(row["arzehPk"]) for row in rows})),
            "forward_rows": str(len(rows)),
            "forward_quantity": display(total_quantity - matching_quantity),
            "forward_matching_quantity": display(matching_quantity),
            "total_quantity": display(total_quantity),
            "forward_matching_share": display(matching_quantity / total_quantity),
            "forward_weighted_price": display(weighted),
            "previous_cash_date_jalali": GAP_LEFT,
            "previous_cash_price": display(left_price),
            "next_cash_date_jalali": GAP_RIGHT,
            "next_cash_price": display(right_price),
            "days_after_previous_cash": display(after),
            "days_before_next_cash": display(before),
            "gap_progress": display(progress),
            "linear_cash_bridge_price": display(bridge),
            "vs_previous_cash_irr_per_kg": display(weighted - left_price),
            "vs_previous_cash_pct": display((weighted / left_price - 1) * 100),
            "vs_next_cash_irr_per_kg": display(weighted - right_price),
            "vs_next_cash_pct": display((weighted / right_price - 1) * 100),
            "vs_linear_bridge_irr_per_kg": display(weighted - bridge),
            "vs_linear_bridge_pct": display((weighted / bridge - 1) * 100),
        })
    if len(output) != 16:
        raise ValueError(f"expected 16 forward-trade dates, found {len(output)}")
    return output


def main() -> None:
    project = Path(__file__).resolve().parents[3]
    rows = build(project)
    output = project / "data/processed/nci_copper_forward_gap.csv"
    temporary = output.with_suffix(output.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(output)
    print(f"Forward-trade dates in cash gap: {len(rows)}")
    print(f"Coverage: {rows[0]['trade_date_jalali']} through {rows[-1]['trade_date_jalali']}")
    print(f"Output: {output}")


if __name__ == "__main__":
    main()
