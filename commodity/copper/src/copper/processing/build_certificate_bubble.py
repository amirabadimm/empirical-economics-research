"""Build the copper-certificate bubble using interpolated IME/LME price ratios."""

from __future__ import annotations

import bisect
import csv
import sys
from datetime import date
from decimal import Decimal, getcontext
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.market_analysis.common import (
    asof_value,
    display,
    number,
    parse_mixed_gregorian,
    read_csv,
)


getcontext().prec = 28

OUTPUT_COLUMNS = [
    "date",
    "certificate_price_irr_per_kg",
    "certificate_trades_volume",
    "certificate_trades_value_irr",
    "lme_source_date",
    "lme_age_days",
    "lme_cash_usd_per_ton",
    "lme_cash_usd_per_kg",
    "usd_source_date",
    "usd_age_days",
    "usd_irr",
    "intrinsic_price_irr_per_kg",
    "physical_ratio",
    "physical_ratio_method",
    "ratio_left_anchor_date",
    "ratio_right_anchor_date",
    "observed_physical_price_irr_per_kg",
    "estimated_physical_price_irr_per_kg",
    "certificate_bubble_irr_per_kg",
    "certificate_bubble_pct",
]


def build(project_dir: Path) -> list[dict[str, str]]:
    copper_dir = project_dir
    certificate_path = project_dir / "data" / "raw" / "certificate" / "copper_certificate_raw.csv"
    physical_path = project_dir / "data" / "processed" / "physical" / "nci_copper_cash_daily.csv"
    lme_path = copper_dir / "data" / "raw" / "lme" / "copper_lme_raw.csv"
    usd_path = project_dir.parents[1] / "shared" / "data" / "raw" / "fx" / "usd_to_rial.csv"
    output_path = project_dir / "data" / "processed" / "bubble" / "copper_certificate_bubble.csv"

    certificate_rows = read_csv(certificate_path)
    physical_rows = read_csv(physical_path)
    lme_rows = read_csv(lme_path)
    usd_rows = read_csv(usd_path)

    certificates: dict[date, dict[str, Decimal]] = {}
    for row in certificate_rows:
        row_date = date.fromisoformat(row["DT"][:10])
        volume = number(row["TradesVolume"], "TradesVolume", str(row_date))
        if volume <= 0:
            continue
        value = number(row["TradesValue"], "TradesValue", str(row_date))
        settlement = number(row["TodaySettlementPrice"], "TodaySettlementPrice", str(row_date))
        calculated = value / volume
        # The API settlement is the volume-weighted price rounded to whole IRR.
        if abs(calculated - settlement) > Decimal("0.500001"):
            raise ValueError(
                f"Certificate VWAP mismatch on {row_date}: {calculated} vs {settlement}"
            )
        certificates[row_date] = {"price": settlement, "volume": volume, "value": value}

    physical: dict[date, Decimal] = {}
    for row in physical_rows:
        row_date = date.fromisoformat(row["physical_trade_date_gregorian"])
        price = number(row["physical_weighted_price"], "physical_weighted_price", str(row_date))
        if price <= 0:
            raise ValueError(f"Non-positive physical price on {row_date}")
        physical[row_date] = price

    lme: dict[date, Decimal] = {}
    for row in lme_rows:
        if row["cash_settlement"].strip() == "-":
            continue
        row_date = date.fromisoformat(row["date"])
        value = number(row["cash_settlement"], "cash_settlement", str(row_date))
        if value <= 0:
            raise ValueError(f"Non-positive LME price on {row_date}")
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

    lme_dates, usd_dates = sorted(lme), sorted(usd)

    def market_inputs(target: date) -> dict[str, Decimal | date | int]:
        lme_date, lme_ton = asof_value(target, lme_dates, lme, "LME")
        usd_date, usd_irr = asof_value(target, usd_dates, usd, "USD/IRR")
        lme_kg = lme_ton / Decimal(1000)
        intrinsic = lme_kg * usd_irr
        return {
            "lme_date": lme_date,
            "lme_age": (target - lme_date).days,
            "lme_ton": lme_ton,
            "lme_kg": lme_kg,
            "usd_date": usd_date,
            "usd_age": (target - usd_date).days,
            "usd_irr": usd_irr,
            "intrinsic": intrinsic,
        }

    # Only physical trades occurring on certificate trading dates are anchors.
    anchor_dates = sorted(set(certificates) & set(physical))
    if len(anchor_dates) < 2:
        raise ValueError(
            f"At least two exact physical/certificate anchors are required; found {len(anchor_dates)}"
        )
    anchor_ratios: dict[date, Decimal] = {}
    for anchor in anchor_dates:
        intrinsic = market_inputs(anchor)["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        anchor_ratios[anchor] = physical[anchor] / intrinsic

    first_anchor, last_anchor = anchor_dates[0], anchor_dates[-1]
    output: list[dict[str, str]] = []
    for target in sorted(certificates):
        # Linear interpolation is defined only inside the observed anchor range.
        if target < first_anchor or target > last_anchor:
            continue
        position = bisect.bisect_left(anchor_dates, target)
        if position < len(anchor_dates) and anchor_dates[position] == target:
            left = right = target
            ratio = anchor_ratios[target]
            method = "observed"
            observed_price: Decimal | None = physical[target]
        else:
            right = anchor_dates[position]
            left = anchor_dates[position - 1]
            elapsed = Decimal((target - left).days)
            span = Decimal((right - left).days)
            ratio = (
                anchor_ratios[left] + (anchor_ratios[right] - anchor_ratios[left]) * elapsed / span
            )
            method = "linear_interpolation"
            observed_price = None

        inputs = market_inputs(target)
        intrinsic = inputs["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        estimated_physical = ratio * intrinsic
        if observed_price is not None and abs(estimated_physical - observed_price) > Decimal(
            "0.000001"
        ):
            raise ValueError(f"Anchor reconstruction failed on {target}")
        certificate = certificates[target]
        bubble_irr = certificate["price"] - estimated_physical
        bubble_pct = (certificate["price"] / estimated_physical - Decimal(1)) * Decimal(100)
        output.append(
            {
                "date": target.isoformat(),
                "certificate_price_irr_per_kg": display(certificate["price"]),
                "certificate_trades_volume": display(certificate["volume"]),
                "certificate_trades_value_irr": display(certificate["value"]),
                "lme_source_date": str(inputs["lme_date"]),
                "lme_age_days": str(inputs["lme_age"]),
                "lme_cash_usd_per_ton": display(inputs["lme_ton"]),
                "lme_cash_usd_per_kg": display(inputs["lme_kg"]),
                "usd_source_date": str(inputs["usd_date"]),
                "usd_age_days": str(inputs["usd_age"]),
                "usd_irr": display(inputs["usd_irr"]),
                "intrinsic_price_irr_per_kg": display(intrinsic),
                "physical_ratio": display(ratio),
                "physical_ratio_method": method,
                "ratio_left_anchor_date": left.isoformat(),
                "ratio_right_anchor_date": right.isoformat(),
                "observed_physical_price_irr_per_kg": display(observed_price),
                "estimated_physical_price_irr_per_kg": display(estimated_physical),
                "certificate_bubble_irr_per_kg": display(bubble_irr),
                "certificate_bubble_pct": display(bubble_pct),
            }
        )

    if not output:
        raise ValueError("Bubble output is empty")
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
    rows = build(project_dir)
    observed = sum(row["physical_ratio_method"] == "observed" for row in rows)
    interpolated = len(rows) - observed
    print(f"Bubble observations: {len(rows)}")
    print(f"Observed anchors: {observed}")
    print(f"Interpolated days: {interpolated}")
    print(f"Coverage: {rows[0]['date']} through {rows[-1]['date']}")
    print(project_dir / "data" / "processed" / "bubble" / "copper_certificate_bubble.csv")


if __name__ == "__main__":
    main()
