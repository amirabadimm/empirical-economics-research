"""Shared validated inputs for Zinc LME–FX bubble builders."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from decimal import Decimal, getcontext
from pathlib import Path
import sys

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.market_analysis.common import (
    asof_value,
    display,
    number,
    parse_mixed_gregorian,
    read_csv,
    write_atomic,
)


getcontext().prec = 28


@dataclass(frozen=True)
class Inputs:
    certificate: dict[date, dict[str, Decimal]]
    physical: dict[date, dict[str, Decimal]]
    lme: dict[date, Decimal]
    usd: dict[date, Decimal]

    def market(self, target: date) -> dict[str, Decimal | date | int]:
        lme_date, lme_ton = asof_value(target, sorted(self.lme), self.lme, "LME Zinc")
        usd_date, usd_irr = asof_value(target, sorted(self.usd), self.usd, "USD/IRR")
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


def load_inputs(project_dir: Path) -> Inputs:
    certificate_rows = read_csv(
        project_dir / "data" / "raw" / "certificate" / "zinc_certificate_raw.csv"
    )
    physical_rows = read_csv(
        project_dir / "data" / "processed" / "physical" / "zinc_9798_cash_daily.csv"
    )
    lme_rows = read_csv(project_dir / "data" / "raw" / "lme" / "zinc_lme_raw.csv")
    workspace_root = project_dir.parents[1]
    usd_rows = read_csv(workspace_root / "shared" / "data" / "raw" / "fx" / "usd_to_rial.csv")

    certificate: dict[date, dict[str, Decimal]] = {}
    for row in certificate_rows:
        row_date = date.fromisoformat(row["DT"][:10])
        volume = number(row["TradesVolume"], "TradesVolume", str(row_date))
        if volume <= 0:
            continue
        value = number(row["TradesValue"], "TradesValue", str(row_date))
        settlement = number(row["TodaySettlementPrice"], "TodaySettlementPrice", str(row_date))
        if value <= 0 or settlement <= 0:
            raise ValueError(f"Non-positive certificate value/settlement on {row_date}")
        if abs(value / volume - settlement) > Decimal("0.500001"):
            raise ValueError(f"Certificate VWAP mismatch on {row_date}")
        certificate[row_date] = {"price": settlement, "volume": volume, "value": value}

    physical: dict[date, dict[str, Decimal]] = {}
    for row in physical_rows:
        row_date = date.fromisoformat(row["physical_trade_date_gregorian"])
        price = number(row["physical_weighted_price"], "physical_weighted_price", str(row_date))
        quantity = number(row["total_quantity"], "total_quantity", str(row_date))
        if price <= 0 or quantity <= 0:
            raise ValueError(f"Non-positive physical observation on {row_date}")
        physical[row_date] = {"price": price, "quantity": quantity}

    lme: dict[date, Decimal] = {}
    for row in lme_rows:
        if row["cash_settlement"].strip() in {"", "-"}:
            continue
        row_date = date.fromisoformat(row["date"])
        value = number(row["cash_settlement"], "cash_settlement", str(row_date))
        if value <= 0:
            raise ValueError(f"Non-positive LME Zinc cash on {row_date}")
        lme[row_date] = value

    usd: dict[date, Decimal] = {}
    for row in usd_rows:
        row_date = parse_mixed_gregorian(row["date_gr"])
        value = number(row["price_irr"], "price_irr", str(row_date))
        if value <= 0:
            raise ValueError(f"Non-positive USD/IRR on {row_date}")
        if row_date in usd and usd[row_date] != value:
            raise ValueError(f"Conflicting USD/IRR values on {row_date}")
        usd[row_date] = value

    if not certificate or not physical or not lme or not usd:
        raise ValueError("One or more Zinc pipeline inputs are empty")
    return Inputs(certificate=certificate, physical=physical, lme=lme, usd=usd)


COMMON_MARKET_COLUMNS = [
    "lme_source_date",
    "lme_age_days",
    "lme_cash_usd_per_ton",
    "lme_cash_usd_per_kg",
    "usd_source_date",
    "usd_age_days",
    "usd_irr",
    "intrinsic_price_irr_per_kg",
]


def market_columns(market: dict[str, Decimal | date | int]) -> dict[str, str]:
    return {
        "lme_source_date": str(market["lme_date"]),
        "lme_age_days": str(market["lme_age"]),
        "lme_cash_usd_per_ton": display(market["lme_ton"]),
        "lme_cash_usd_per_kg": display(market["lme_kg"]),
        "usd_source_date": str(market["usd_date"]),
        "usd_age_days": str(market["usd_age"]),
        "usd_irr": display(market["usd_irr"]),
        "intrinsic_price_irr_per_kg": display(market["intrinsic"]),
    }
