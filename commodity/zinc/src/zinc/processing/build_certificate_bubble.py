"""Build the primary Zinc certificate bubble from interpolated physical ratios."""

from __future__ import annotations

import bisect
from decimal import Decimal
from pathlib import Path

from bubble_common import (
    COMMON_MARKET_COLUMNS,
    display,
    load_inputs,
    market_columns,
    write_atomic,
)


OUTPUT_COLUMNS = [
    "date", "certificate_price_irr_per_kg", "certificate_trades_volume",
    "certificate_trades_value_irr", *COMMON_MARKET_COLUMNS,
    "physical_ratio", "physical_ratio_method", "ratio_left_anchor_date",
    "ratio_right_anchor_date", "observed_physical_price_irr_per_kg",
    "estimated_physical_price_irr_per_kg", "certificate_bubble_irr_per_kg",
    "certificate_bubble_pct",
]


def build(project_dir: Path) -> list[dict[str, str]]:
    inputs = load_inputs(project_dir)
    anchor_dates = sorted(set(inputs.certificate) & set(inputs.physical))
    if len(anchor_dates) < 2:
        raise ValueError(f"At least two exact physical/certificate anchors are required; found {len(anchor_dates)}")

    anchor_ratios: dict[object, Decimal] = {}
    for anchor in anchor_dates:
        intrinsic = inputs.market(anchor)["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        anchor_ratios[anchor] = inputs.physical[anchor]["price"] / intrinsic

    first_anchor, last_anchor = anchor_dates[0], anchor_dates[-1]
    output: list[dict[str, str]] = []
    for target in sorted(inputs.certificate):
        if target < first_anchor or target > last_anchor:
            continue
        position = bisect.bisect_left(anchor_dates, target)
        if position < len(anchor_dates) and anchor_dates[position] == target:
            left = right = target
            ratio = anchor_ratios[target]
            method = "observed"
            observed_price: Decimal | None = inputs.physical[target]["price"]
        else:
            right = anchor_dates[position]
            left = anchor_dates[position - 1]
            weight = Decimal((target - left).days) / Decimal((right - left).days)
            ratio = anchor_ratios[left] + weight * (anchor_ratios[right] - anchor_ratios[left])
            method = "linear_interpolation"
            observed_price = None

        market = inputs.market(target)
        intrinsic = market["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        estimated_physical = ratio * intrinsic
        if observed_price is not None and abs(estimated_physical - observed_price) > Decimal("0.000001"):
            raise ValueError(f"Anchor reconstruction failed on {target}")
        certificate = inputs.certificate[target]
        bubble_irr = certificate["price"] - estimated_physical
        bubble_pct = (certificate["price"] / estimated_physical - 1) * 100
        output.append({
            "date": target.isoformat(),
            "certificate_price_irr_per_kg": display(certificate["price"]),
            "certificate_trades_volume": display(certificate["volume"]),
            "certificate_trades_value_irr": display(certificate["value"]),
            **market_columns(market),
            "physical_ratio": display(ratio),
            "physical_ratio_method": method,
            "ratio_left_anchor_date": left.isoformat(),
            "ratio_right_anchor_date": right.isoformat(),
            "observed_physical_price_irr_per_kg": display(observed_price),
            "estimated_physical_price_irr_per_kg": display(estimated_physical),
            "certificate_bubble_irr_per_kg": display(bubble_irr),
            "certificate_bubble_pct": display(bubble_pct),
        })

    if not output:
        raise ValueError("Primary Zinc bubble output is empty")
    write_atomic(
        project_dir / "data" / "processed" / "zinc_certificate_bubble.csv",
        OUTPUT_COLUMNS,
        output,
    )
    return output


def main() -> None:
    project_dir = Path(__file__).resolve().parents[3]
    rows = build(project_dir)
    observed = sum(row["physical_ratio_method"] == "observed" for row in rows)
    print(f"Bubble observations: {len(rows)}")
    print(f"Observed anchors: {observed}")
    print(f"Interpolated days: {len(rows) - observed}")
    print(f"Coverage: {rows[0]['date']} through {rows[-1]['date']}")


if __name__ == "__main__":
    main()
