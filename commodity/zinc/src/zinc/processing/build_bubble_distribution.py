"""Build standardized empirical distributions for every zinc bubble series."""

import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.market_analysis.bubble_distribution import BubbleSeriesSpec
from shared.market_analysis.bubble_percentiles import build_project_distributions


PROJECT_DIR = Path(__file__).resolve().parents[3]
HALF_LIFE_DAYS = 90.0  # Calendar-day decay; configurable research assumption.
SPECS = (
    BubbleSeriesSpec("certificate_physical", "certificate_vs_physical", "Certificate vs physical", "zinc_certificate_bubble.csv", "date", "certificate_bubble_pct", point_method_column="physical_ratio_method"),
    BubbleSeriesSpec("certificate_intrinsic", "certificate_vs_intrinsic", "Certificate vs intrinsic", "certificate_vs_intrinsic_bubble.csv", "date", "certificate_vs_intrinsic_bubble_pct"),
    BubbleSeriesSpec("physical_intrinsic", "physical_vs_intrinsic", "Physical vs intrinsic", "physical_vs_intrinsic_bubble.csv", "date", "physical_vs_intrinsic_bubble_pct"),
)


def build():
    return build_project_distributions(project_dir=PROJECT_DIR, commodity="zinc", specs=SPECS, half_life_days=HALF_LIFE_DAYS)


if __name__ == "__main__":
    result = build()
    print(f"Built {len(result)} zinc distribution rows")
