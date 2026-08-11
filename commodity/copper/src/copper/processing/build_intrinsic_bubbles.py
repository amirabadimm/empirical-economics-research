"""Build physical-vs-intrinsic and certificate-vs-intrinsic copper datasets."""

from __future__ import annotations

import csv
from datetime import date
from decimal import Decimal
from pathlib import Path

from build_certificate_bubble import (
    asof_value,
    display,
    number,
    parse_mixed_gregorian,
    read_csv,
)


COMMON_COLUMNS = [
    "date",
    "lme_source_date",
    "lme_age_days",
    "lme_cash_usd_per_ton",
    "lme_cash_usd_per_kg",
    "usd_source_date",
    "usd_age_days",
    "usd_irr",
    "intrinsic_price_irr_per_kg",
]

PHYSICAL_COLUMNS = [
    "date",
    "physical_price_irr_per_kg",
    "physical_total_quantity",
    *COMMON_COLUMNS[1:],
    "physical_to_intrinsic_ratio",
    "physical_vs_intrinsic_irr_per_kg",
    "physical_vs_intrinsic_bubble_pct",
    "is_certificate_trade_date",
    "is_main_exact_anchor",
]

CERTIFICATE_COLUMNS = [
    "date",
    "certificate_price_irr_per_kg",
    "certificate_trades_volume",
    "certificate_trades_value_irr",
    *COMMON_COLUMNS[1:],
    "certificate_to_intrinsic_ratio",
    "certificate_vs_intrinsic_irr_per_kg",
    "certificate_vs_intrinsic_bubble_pct",
    "is_physical_trade_date",
    "is_main_exact_anchor",
]


def write_atomic(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def build(project_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    copper_dir = project_dir
    certificate_rows = read_csv(
        project_dir / "data" / "raw" / "certificate" / "copper_certificate_raw.csv"
    )
    physical_rows = read_csv(
        project_dir / "data" / "processed" / "nci_copper_cash_daily.csv"
    )
    lme_rows = read_csv(copper_dir / "data" / "raw" / "lme" / "copper_lme_raw.csv")
    usd_rows = read_csv(copper_dir / "data" / "raw" / "fx" / "usd_to_rial.csv")

    certificate: dict[date, dict[str, Decimal]] = {}
    for row in certificate_rows:
        row_date = date.fromisoformat(row["DT"][:10])
        volume = number(row["TradesVolume"], "TradesVolume", str(row_date))
        if volume <= 0:
            continue
        value = number(row["TradesValue"], "TradesValue", str(row_date))
        settlement = number(
            row["TodaySettlementPrice"], "TodaySettlementPrice", str(row_date)
        )
        price = value / volume
        if abs(price - settlement) > Decimal("0.500001"):
            raise ValueError(f"Certificate VWAP mismatch on {row_date}")
        certificate[row_date] = {"price": settlement, "volume": volume, "value": value}

    physical: dict[date, dict[str, Decimal]] = {}
    for row in physical_rows:
        row_date = date.fromisoformat(row["physical_trade_date_gregorian"])
        price = number(
            row["physical_weighted_price"], "physical_weighted_price", str(row_date)
        )
        quantity = number(row["total_quantity"], "total_quantity", str(row_date))
        if price <= 0 or quantity <= 0:
            raise ValueError(f"Non-positive physical observation on {row_date}")
        physical[row_date] = {"price": price, "quantity": quantity}

    lme: dict[date, Decimal] = {}
    for row in lme_rows:
        if row["cash_settlement"].strip() == "-":
            continue
        row_date = date.fromisoformat(row["date"])
        lme[row_date] = number(
            row["cash_settlement"], "cash_settlement", str(row_date)
        )

    usd: dict[date, Decimal] = {}
    for row in usd_rows:
        row_date = parse_mixed_gregorian(row["date_gr"])
        value = number(row["price_irr"], "price_irr", str(row_date))
        if row_date in usd and usd[row_date] != value:
            raise ValueError(f"Conflicting USD values on {row_date}")
        usd[row_date] = value

    lme_dates, usd_dates = sorted(lme), sorted(usd)

    def inputs(target: date) -> dict[str, Decimal | date | int]:
        lme_date, lme_ton = asof_value(target, lme_dates, lme, "LME")
        usd_date, usd_irr = asof_value(target, usd_dates, usd, "USD/IRR")
        lme_kg = lme_ton / Decimal(1000)
        return {
            "lme_date": lme_date,
            "lme_age": (target - lme_date).days,
            "lme_ton": lme_ton,
            "lme_kg": lme_kg,
            "usd_date": usd_date,
            "usd_age": (target - usd_date).days,
            "usd_irr": usd_irr,
            "intrinsic": lme_kg * usd_irr,
        }

    certificate_dates = set(certificate)
    physical_dates = set(physical)
    anchors = certificate_dates & physical_dates
    if len(anchors) < 2:
        raise ValueError(f"At least two exact anchors are required; found {len(anchors)}")

    physical_output: list[dict[str, str]] = []
    for target in sorted(physical):
        market = inputs(target)
        intrinsic = market["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        price = physical[target]["price"]
        ratio = price / intrinsic
        physical_output.append({
            "date": target.isoformat(),
            "physical_price_irr_per_kg": display(price),
            "physical_total_quantity": display(physical[target]["quantity"]),
            "lme_source_date": str(market["lme_date"]),
            "lme_age_days": str(market["lme_age"]),
            "lme_cash_usd_per_ton": display(market["lme_ton"]),
            "lme_cash_usd_per_kg": display(market["lme_kg"]),
            "usd_source_date": str(market["usd_date"]),
            "usd_age_days": str(market["usd_age"]),
            "usd_irr": display(market["usd_irr"]),
            "intrinsic_price_irr_per_kg": display(intrinsic),
            "physical_to_intrinsic_ratio": display(ratio),
            "physical_vs_intrinsic_irr_per_kg": display(price - intrinsic),
            "physical_vs_intrinsic_bubble_pct": display((ratio - 1) * 100),
            "is_certificate_trade_date": str(int(target in certificate_dates)),
            "is_main_exact_anchor": str(int(target in anchors)),
        })

    certificate_output: list[dict[str, str]] = []
    for target in sorted(certificate):
        market = inputs(target)
        intrinsic = market["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        price = certificate[target]["price"]
        ratio = price / intrinsic
        certificate_output.append({
            "date": target.isoformat(),
            "certificate_price_irr_per_kg": display(price),
            "certificate_trades_volume": display(certificate[target]["volume"]),
            "certificate_trades_value_irr": display(certificate[target]["value"]),
            "lme_source_date": str(market["lme_date"]),
            "lme_age_days": str(market["lme_age"]),
            "lme_cash_usd_per_ton": display(market["lme_ton"]),
            "lme_cash_usd_per_kg": display(market["lme_kg"]),
            "usd_source_date": str(market["usd_date"]),
            "usd_age_days": str(market["usd_age"]),
            "usd_irr": display(market["usd_irr"]),
            "intrinsic_price_irr_per_kg": display(intrinsic),
            "certificate_to_intrinsic_ratio": display(ratio),
            "certificate_vs_intrinsic_irr_per_kg": display(price - intrinsic),
            "certificate_vs_intrinsic_bubble_pct": display((ratio - 1) * 100),
            "is_physical_trade_date": str(int(target in physical_dates)),
            "is_main_exact_anchor": str(int(target in anchors)),
        })

    processed = project_dir / "data" / "processed"
    write_atomic(
        processed / "physical_vs_intrinsic_bubble.csv",
        PHYSICAL_COLUMNS,
        physical_output,
    )
    write_atomic(
        processed / "certificate_vs_intrinsic_bubble.csv",
        CERTIFICATE_COLUMNS,
        certificate_output,
    )
    return physical_output, certificate_output


def main() -> None:
    project_dir = Path(__file__).resolve().parents[3]
    physical, certificate = build(project_dir)
    print(f"Physical vs intrinsic rows: {len(physical)}")
    print(f"Certificate vs intrinsic rows: {len(certificate)}")
    print(f"Exact anchors: {sum(r['is_main_exact_anchor'] == '1' for r in physical)}")
    print(project_dir / "data" / "processed")


if __name__ == "__main__":
    main()
