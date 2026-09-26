"""Build the copper-certificate bubble using interpolated IME/LME price ratios."""

from __future__ import annotations

import bisect
import sys
from datetime import date
from decimal import Decimal, getcontext
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from valuation_inputs import load_inputs, write_atomic

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


def build(project_dir: Path, prepared=None) -> list[dict[str, str]]:
    certificates, physical_records, market_inputs = prepared if prepared is not None else load_inputs(project_dir)
    physical = {day: row['price'] for day, row in physical_records.items()}
    output_path = project_dir / 'data/processed/bubble/copper_certificate_bubble.csv'

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
    write_atomic(output_path, OUTPUT_COLUMNS, output)
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
