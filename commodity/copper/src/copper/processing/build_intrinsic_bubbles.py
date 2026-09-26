"""Build physical-vs-intrinsic and certificate-vs-intrinsic copper datasets."""

from __future__ import annotations

from datetime import date
from decimal import Decimal
from pathlib import Path

from valuation_inputs import load_inputs, display, write_atomic


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
    "physical_trades_value_irr",
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


def build(project_dir: Path, prepared=None) -> tuple[list[dict[str, str]], list[dict[str, str]]]:
    certificate, physical, inputs = prepared if prepared is not None else load_inputs(project_dir)

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
            "physical_trades_value_irr": display(physical[target]["value"]),
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

    processed = project_dir / "data" / "processed" / "bubble"
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
    print(project_dir / "data" / "processed" / "bubble")


if __name__ == "__main__":
    main()
