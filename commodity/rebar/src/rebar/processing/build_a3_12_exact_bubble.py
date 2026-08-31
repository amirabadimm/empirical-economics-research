"""Build the intentional cross-diameter certificate-versus-A3/12 cash diagnostic."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.rebar.src.rebar.processing.build_a3_18_exact_bubble import (  # noqa: E402
    CERTIFICATE_PATH,
    PHYSICAL_PATH,
    build_exact_bubble,
    write_atomic,
)
from commodity.rebar.src.rebar.processing.rebar_scope import (  # noqa: E402
    A3_12_PRODUCT,
    is_a3_12_straight_rebar,
)


PROJECT_DIR = Path(__file__).resolve().parents[3]
OUTPUT_PATH = (
    PROJECT_DIR / "data" / "processed" / "bubble" / "rebar_a3_12_exact_date_bubble.csv"
)


def build(physical_raw: pd.DataFrame, certificate_raw: pd.DataFrame) -> pd.DataFrame:
    """Build the A3/12 cross-diameter diagnostic with the shared exact-date engine."""
    return build_exact_bubble(
        physical_raw,
        certificate_raw,
        product_scope=A3_12_PRODUCT,
        product_predicate=is_a3_12_straight_rebar,
        comparability_status="intentional_cross_diameter_diagnostic_not_underlying_match",
        alignment_method="exact_date_observed_cash_a3_12_cross_diameter",
    )


def main() -> None:
    physical = pd.read_csv(PHYSICAL_PATH, encoding="utf-8-sig", low_memory=False)
    certificate = pd.read_csv(CERTIFICATE_PATH, encoding="utf-8-sig", low_memory=False)
    output = build(physical, certificate)
    write_atomic(output, OUTPUT_PATH)
    print(f"Built {A3_12_PRODUCT} cross-diameter certificate diagnostic: {len(output)} observations")
    print(f"Coverage: {output.date.iloc[0]} through {output.date.iloc[-1]}")
    print(f"Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
