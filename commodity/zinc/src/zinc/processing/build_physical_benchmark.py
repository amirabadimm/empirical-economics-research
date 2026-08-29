"""Build the daily 99.97+99.98 zinc-ingot cash benchmark."""

from __future__ import annotations

import csv
import re
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.ime_data.ime_physical_collector import jalali_to_gregorian  # noqa: E402


TARGET_GRADES = {"99.97", "99.98"}
CASH = "نقدی"
MATCHING = "نقدی (مچینگ)"
TARGET_CONTRACTS = {CASH, MATCHING}
OUTPUT_COLUMNS = [
    "physical_trade_date_jalali",
    "physical_trade_date_gregorian",
    "grades",
    "symbols",
    "producers",
    "cash_trade_rows",
    "matching_trade_rows",
    "total_trade_rows",
    "grade_99_97_trade_rows",
    "grade_99_98_trade_rows",
    "cash_quantity",
    "matching_quantity",
    "grade_99_97_quantity",
    "grade_99_98_quantity",
    "total_quantity",
    "matching_quantity_share",
    "grade_99_97_quantity_share",
    "grade_99_98_quantity_share",
    "grade_99_97_weighted_price",
    "grade_99_98_weighted_price",
    "physical_weighted_price",
    "price_source_field",
    "quantity_source_field",
]


def normalize_fa(value: str) -> str:
    return str(value or "").replace("ي", "ی").replace("ك", "ک").strip()


def extract_grade(goods_name: str) -> str | None:
    name = normalize_fa(goods_name)
    if "شمش روی" not in name:
        return None
    match = re.search(r"(\d{2}(?:\.\d+)?)", name)
    if not match:
        return None
    return f"{Decimal(match.group(1)):.2f}"


def number(value: str, field: str, trade_date: str) -> Decimal:
    try:
        result = Decimal(str(value).replace(",", "").strip() or "0")
    except InvalidOperation as exc:
        raise ValueError(f"Invalid {field} on {trade_date}: {value!r}") from exc
    if result < 0:
        raise ValueError(f"Negative {field} on {trade_date}: {result}")
    return result


def jalali_dates(value: str) -> tuple[str, str]:
    parts = str(value).replace("-", "/").split("/")
    if len(parts) != 3:
        raise ValueError(f"Unexpected Jalali date: {value!r}")
    jy, jm, jd = map(int, parts)
    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
    return f"{jy:04d}/{jm:02d}/{jd:02d}", f"{gy:04d}-{gm:02d}-{gd:02d}"


def display(value: Decimal | None) -> str:
    if value is None:
        return ""
    if value == value.to_integral_value():
        return str(int(value))
    return format(value.normalize(), "f")


def weighted_price(rows: list[dict[str, object]]) -> Decimal | None:
    quantity = sum((row["quantity"] for row in rows), Decimal(0))
    if quantity <= 0:
        return None
    return sum((row["price"] * row["quantity"] for row in rows), Decimal(0)) / quantity


def build(raw_path: Path, output_path: Path) -> list[dict[str, str]]:
    with raw_path.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if not raw_rows:
        raise ValueError(f"No raw rows found in {raw_path}")

    grouped: dict[str, list[dict[str, object]]] = defaultdict(list)
    for row in raw_rows:
        grade = extract_grade(row["GoodsName"])
        contract = normalize_fa(row["ContractType"])
        if grade not in TARGET_GRADES or contract not in TARGET_CONTRACTS:
            continue
        trade_date, _ = jalali_dates(row["date"])
        quantity = number(row["Quantity"], "Quantity", trade_date)
        price = number(row["Price"], "Price", trade_date)
        if quantity > 0 and price > 0:
            grouped[trade_date].append({
                "grade": grade,
                "contract": contract,
                "quantity": quantity,
                "price": price,
                "symbol": str(row["Symbol"]).strip(),
                "producer": normalize_fa(row["ProducerName"]),
            })

    output: list[dict[str, str]] = []
    for trade_date in sorted(grouped):
        rows = grouped[trade_date]
        cash = [row for row in rows if row["contract"] == CASH]
        matching = [row for row in rows if row["contract"] == MATCHING]
        grade_97 = [row for row in rows if row["grade"] == "99.97"]
        grade_98 = [row for row in rows if row["grade"] == "99.98"]
        cash_q = sum((row["quantity"] for row in cash), Decimal(0))
        matching_q = sum((row["quantity"] for row in matching), Decimal(0))
        q97 = sum((row["quantity"] for row in grade_97), Decimal(0))
        q98 = sum((row["quantity"] for row in grade_98), Decimal(0))
        total_q = cash_q + matching_q
        if total_q <= 0 or q97 + q98 != total_q:
            raise ValueError(f"Invalid grade/contract quantity reconciliation on {trade_date}")
        _, gregorian = jalali_dates(trade_date)
        output.append({
            "physical_trade_date_jalali": trade_date,
            "physical_trade_date_gregorian": gregorian,
            "grades": "|".join(sorted({str(row["grade"]) for row in rows})),
            "symbols": "|".join(sorted({str(row["symbol"]) for row in rows})),
            "producers": "|".join(sorted({str(row["producer"]) for row in rows})),
            "cash_trade_rows": str(len(cash)),
            "matching_trade_rows": str(len(matching)),
            "total_trade_rows": str(len(rows)),
            "grade_99_97_trade_rows": str(len(grade_97)),
            "grade_99_98_trade_rows": str(len(grade_98)),
            "cash_quantity": display(cash_q),
            "matching_quantity": display(matching_q),
            "grade_99_97_quantity": display(q97),
            "grade_99_98_quantity": display(q98),
            "total_quantity": display(total_q),
            "matching_quantity_share": display(matching_q / total_q),
            "grade_99_97_quantity_share": display(q97 / total_q),
            "grade_99_98_quantity_share": display(q98 / total_q),
            "grade_99_97_weighted_price": display(weighted_price(grade_97)),
            "grade_99_98_weighted_price": display(weighted_price(grade_98)),
            "physical_weighted_price": display(weighted_price(rows)),
            "price_source_field": "Price",
            "quantity_source_field": "Quantity",
        })

    if not output:
        raise ValueError("No positive 99.97/99.98 cash trades were found")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    temporary = output_path.with_suffix(output_path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=OUTPUT_COLUMNS)
        writer.writeheader()
        writer.writerows(output)
    temporary.replace(output_path)
    return output


def main() -> None:
    project_dir = Path(__file__).resolve().parents[3]
    rows = build(
        project_dir / "data" / "raw" / "physical" / "zinc_physical_raw.csv",
        project_dir / "data" / "processed" / "physical" / "zinc_9798_cash_daily.csv",
    )
    print(f"Daily traded observations: {len(rows)}")
    print(f"Coverage: {rows[0]['physical_trade_date_jalali']} through {rows[-1]['physical_trade_date_jalali']}")


if __name__ == "__main__":
    main()
