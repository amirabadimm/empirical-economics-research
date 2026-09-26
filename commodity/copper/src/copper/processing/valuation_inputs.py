"""Single copper input-preparation and intrinsic-value contract.

No files are written here. Both production builders use these identical inputs.
"""
from datetime import date
from decimal import Decimal, getcontext
from pathlib import Path
import sys

WORKSPACE = Path(__file__).resolve().parents[5]
if str(WORKSPACE) not in sys.path:
    sys.path.insert(0, str(WORKSPACE))
from shared.market_analysis.common import asof_value, display, number, parse_mixed_gregorian, read_csv, write_atomic

getcontext().prec = 28


def load_inputs(project_dir: Path):
    copper_dir = project_dir
    certificate_rows = read_csv(
        project_dir / "data" / "raw" / "certificate" / "copper_certificate_raw.csv"
    )
    physical_rows = read_csv(
        project_dir / "data" / "processed" / "physical" / "nci_copper_cash_daily.csv"
    )
    lme_rows = read_csv(copper_dir / "data" / "raw" / "lme" / "copper_lme_raw.csv")
    usd_rows = read_csv(
        project_dir.parents[1] / "shared" / "data" / "raw" / "fx" / "usd_to_rial.csv"
    )

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
        value = number(
            row["physical_trades_value_irr"], "physical_trades_value_irr", str(row_date)
        )
        if price <= 0 or quantity <= 0 or value <= 0:
            raise ValueError(f"Non-positive physical observation on {row_date}")
        physical[row_date] = {"price": price, "quantity": quantity, "value": value}

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

    for label, series in [('LME', lme), ('USD/IRR', usd)]:
        if not series or any(not v.is_finite() or v <= 0 for v in series.values()):
            raise ValueError(f'Invalid or non-positive {label} input')
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

    return certificate, physical, inputs
