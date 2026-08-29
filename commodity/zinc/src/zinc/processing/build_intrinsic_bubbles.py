"""Build direct physical/intrinsic and certificate/intrinsic Zinc bubbles."""

from __future__ import annotations

from decimal import Decimal
from pathlib import Path

from bubble_common import (
    COMMON_MARKET_COLUMNS,
    display,
    load_inputs,
    market_columns,
    write_atomic,
)


PHYSICAL_COLUMNS = [
    "date", "physical_price_irr_per_kg", "physical_total_quantity",
    *COMMON_MARKET_COLUMNS,
    "physical_to_intrinsic_ratio", "physical_vs_intrinsic_irr_per_kg",
    "physical_vs_intrinsic_bubble_pct", "is_certificate_trade_date",
    "is_main_exact_anchor",
]
CERTIFICATE_COLUMNS = [
    "date", "certificate_price_irr_per_kg", "certificate_trades_volume",
    "certificate_trades_value_irr", *COMMON_MARKET_COLUMNS,
    "certificate_to_intrinsic_ratio", "certificate_vs_intrinsic_irr_per_kg",
    "certificate_vs_intrinsic_bubble_pct", "is_physical_trade_date",
    "is_main_exact_anchor",
]


def build(project_dir: Path) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    inputs = load_inputs(project_dir)
    certificate_dates = set(inputs.certificate)
    physical_dates = set(inputs.physical)
    anchors = certificate_dates & physical_dates
    if len(anchors) < 2:
        raise ValueError(f"At least two exact anchors are required; found {len(anchors)}")

    physical_output: list[dict[str, str]] = []
    for target in sorted(inputs.physical):
        market = inputs.market(target)
        intrinsic = market["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        price = inputs.physical[target]["price"]
        ratio = price / intrinsic
        physical_output.append({
            "date": target.isoformat(),
            "physical_price_irr_per_kg": display(price),
            "physical_total_quantity": display(inputs.physical[target]["quantity"]),
            **market_columns(market),
            "physical_to_intrinsic_ratio": display(ratio),
            "physical_vs_intrinsic_irr_per_kg": display(price - intrinsic),
            "physical_vs_intrinsic_bubble_pct": display((ratio - 1) * 100),
            "is_certificate_trade_date": str(int(target in certificate_dates)),
            "is_main_exact_anchor": str(int(target in anchors)),
        })

    certificate_output: list[dict[str, str]] = []
    for target in sorted(inputs.certificate):
        market = inputs.market(target)
        intrinsic = market["intrinsic"]
        assert isinstance(intrinsic, Decimal)
        price = inputs.certificate[target]["price"]
        ratio = price / intrinsic
        certificate_output.append({
            "date": target.isoformat(),
            "certificate_price_irr_per_kg": display(price),
            "certificate_trades_volume": display(inputs.certificate[target]["volume"]),
            "certificate_trades_value_irr": display(inputs.certificate[target]["value"]),
            **market_columns(market),
            "certificate_to_intrinsic_ratio": display(ratio),
            "certificate_vs_intrinsic_irr_per_kg": display(price - intrinsic),
            "certificate_vs_intrinsic_bubble_pct": display((ratio - 1) * 100),
            "is_physical_trade_date": str(int(target in physical_dates)),
            "is_main_exact_anchor": str(int(target in anchors)),
        })

    processed = project_dir / "data" / "processed" / "bubble"
    write_atomic(processed / "physical_vs_intrinsic_bubble.csv", PHYSICAL_COLUMNS, physical_output)
    write_atomic(processed / "certificate_vs_intrinsic_bubble.csv", CERTIFICATE_COLUMNS, certificate_output)
    return physical_output, certificate_output


def main() -> None:
    project_dir = Path(__file__).resolve().parents[3]
    physical, certificate = build(project_dir)
    print(f"Physical vs intrinsic rows: {len(physical)}")
    print(f"Certificate vs intrinsic rows: {len(certificate)}")
    print(f"Exact anchors: {sum(row['is_main_exact_anchor'] == '1' for row in physical)}")


if __name__ == "__main__":
    main()
