"""Build the daily NCI copper-cathode cash benchmark from canonical raw data."""

from __future__ import annotations

import csv
import sys
from collections import defaultdict
from decimal import Decimal, InvalidOperation
from pathlib import Path

PROJECT_SRC = Path(__file__).resolve().parents[2]
if str(PROJECT_SRC) not in sys.path:
    sys.path.insert(0, str(PROJECT_SRC))

from copper.collectors.physical import gregorian_to_jalali, jalali_to_gregorian  # noqa: E402


TARGET_SYMBOLS = {"NCI-CCAA-00", "NCI-OACCAA-00"}
CASH = "نقدی"
MATCHING = "نقدی (مچینگ)"
TARGET_CONTRACTS = {CASH, MATCHING}
OUTPUT_COLUMNS = [
    "physical_trade_date_jalali",
    "physical_trade_date_gregorian",
    "symbols",
    "cash_trade_rows",
    "matching_trade_rows",
    "total_trade_rows",
    "cash_quantity",
    "matching_quantity",
    "total_quantity",
    "matching_quantity_share",
    "physical_weighted_price",
    "cash_trades_value_irr",
    "matching_trades_value_irr",
    "physical_trades_value_irr",
    "quantity_source_field",
    "trades_value_source_field",
]


def decimal_value(value: str, field: str, trade_date: str) -> Decimal:
    try:
        result = Decimal(str(value).replace(",", "").strip() or "0")
    except InvalidOperation as exc:
        raise ValueError(f"Invalid {field} on {trade_date}: {value!r}") from exc
    if result < 0:
        raise ValueError(f"Negative {field} on {trade_date}: {result}")
    return result


def normalize_persian(value: str) -> str:
    return value.replace("ي", "ی").replace("ك", "ک").strip()


def jalali_iso(value: str) -> tuple[str, str]:
    parts = value.replace("-", "/").split("/")
    if len(parts) != 3:
        raise ValueError(f"Unexpected Jalali date: {value!r}")
    jy, jm, jd = map(int, parts)
    gy, gm, gd = jalali_to_gregorian(jy, jm, jd)
    # Round-trip validation catches malformed source dates.
    if gregorian_to_jalali(gy, gm, gd) != (jy, jm, jd):
        raise ValueError(f"Jalali date failed round-trip validation: {value!r}")
    return f"{jy:04d}/{jm:02d}/{jd:02d}", f"{gy:04d}-{gm:02d}-{gd:02d}"


def display_number(value: Decimal | None) -> str:
    if value is None:
        return ""
    if value == value.to_integral_value():
        return str(int(value))
    return format(value.normalize(), "f")


def weighted_price(rows: list[tuple[Decimal, Decimal]]) -> Decimal | None:
    quantity = sum((q for _, q in rows), Decimal(0))
    if quantity == 0:
        return None
    return sum((price * q for price, q in rows), Decimal(0)) / quantity


def build(raw_path: Path, output_path: Path) -> list[dict[str, str]]:
    with raw_path.open("r", encoding="utf-8-sig", newline="") as handle:
        raw_rows = list(csv.DictReader(handle))
    if not raw_rows:
        raise ValueError(f"No raw rows found in {raw_path}")

    grouped: dict[str, dict[str, list[tuple[Decimal, Decimal, Decimal, str]]]] = defaultdict(
        lambda: {CASH: [], MATCHING: []}
    )
    for row in raw_rows:
        trade_date, _ = jalali_iso(row["date"])
        symbol = row["Symbol"].strip()
        contract = normalize_persian(row["ContractType"])
        goods = normalize_persian(row["GoodsName"])
        if goods != "مس کاتد" or symbol not in TARGET_SYMBOLS or contract not in TARGET_CONTRACTS:
            raise ValueError(
                f"Canonical raw scope violation on {trade_date}: "
                f"goods={goods!r}, symbol={symbol!r}, contract={contract!r}"
            )
        quantity = decimal_value(row["Quantity"], "Quantity", trade_date)
        price = decimal_value(row["Price"], "Price", trade_date)
        source_total = decimal_value(row["TotalPrice"], "TotalPrice", trade_date)
        # Offers without an executed quantity/price remain in raw but are not trades.
        if quantity > 0 and price > 0:
            if source_total <= 0:
                raise ValueError(f"Positive trade with non-positive TotalPrice on {trade_date}")
            # IME reports Price in IRR/kg, Quantity in tonnes, and TotalPrice in
            # million IRR. Price is rounded, so validate with a small tolerance.
            implied_source_total = price * quantity
            relative_error = abs(source_total - implied_source_total) / source_total
            if relative_error > Decimal("0.00002"):
                raise ValueError(
                    f"TotalPrice mismatch on {trade_date}: source={source_total}, "
                    f"price_x_quantity={implied_source_total}"
                )
            grouped[trade_date][contract].append((price, quantity, source_total, symbol))

    output: list[dict[str, str]] = []
    for trade_date in sorted(grouped):
        cash = grouped[trade_date][CASH]
        matching = grouped[trade_date][MATCHING]
        combined = cash + matching
        if not combined:
            continue
        cash_pairs = [(p, q) for p, q, _, _ in cash]
        matching_pairs = [(p, q) for p, q, _, _ in matching]
        combined_pairs = cash_pairs + matching_pairs
        cash_q = sum((q for _, q in cash_pairs), Decimal(0))
        matching_q = sum((q for _, q in matching_pairs), Decimal(0))
        total_q = cash_q + matching_q
        cash_price = weighted_price(cash_pairs)
        matching_price = weighted_price(matching_pairs)
        total_price = weighted_price(combined_pairs)
        cash_value_irr = sum((value for _, _, value, _ in cash), Decimal(0)) * 1000000
        matching_value_irr = sum((value for _, _, value, _ in matching), Decimal(0)) * 1000000
        total_value_irr = cash_value_irr + matching_value_irr
        if cash_price is not None and matching_price is not None and cash_price != matching_price:
            raise ValueError(
                f"Cash and matching prices diverged on {trade_date}: "
                f"cash={cash_price}, matching={matching_price}. Review the one-price rule."
            )
        _, gregorian = jalali_iso(trade_date)
        output.append({
            "physical_trade_date_jalali": trade_date,
            "physical_trade_date_gregorian": gregorian,
            "symbols": "|".join(sorted({symbol for _, _, _, symbol in combined})),
            "cash_trade_rows": str(len(cash)),
            "matching_trade_rows": str(len(matching)),
            "total_trade_rows": str(len(combined)),
            "cash_quantity": display_number(cash_q),
            "matching_quantity": display_number(matching_q),
            "total_quantity": display_number(total_q),
            "matching_quantity_share": display_number(matching_q / total_q),
            "physical_weighted_price": display_number(total_price),
            "cash_trades_value_irr": display_number(cash_value_irr),
            "matching_trades_value_irr": display_number(matching_value_irr),
            "physical_trades_value_irr": display_number(total_value_irr),
            "quantity_source_field": "Quantity",
            "trades_value_source_field": "TotalPrice (million IRR) x 1,000,000",
        })

    if not output:
        raise ValueError("No positive-quantity, positive-price trades were found")
    if any(Decimal(row["total_quantity"]) <= 0 for row in output):
        raise ValueError("Non-positive daily total quantity found")

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
    raw_path = project_dir / "data" / "raw" / "physical" / "copper_cathode_physical_raw.csv"
    output_path = project_dir / "data" / "processed" / "physical" / "nci_copper_cash_daily.csv"
    rows = build(raw_path, output_path)
    print(f"Daily traded observations: {len(rows)}")
    print(f"Coverage: {rows[0]['physical_trade_date_jalali']} through {rows[-1]['physical_trade_date_jalali']}")
    print(f"Output: {output_path}")


if __name__ == "__main__":
    main()
