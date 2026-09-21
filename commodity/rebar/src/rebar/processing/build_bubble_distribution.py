"""Build standardized empirical distributions for computed rebar diagnostics."""

import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.market_analysis.bubble_distribution import BubbleSeriesSpec, build_project_distributions


PROJECT_DIR = Path(__file__).resolve().parents[3]
SPECS = (
    BubbleSeriesSpec("a3_18_certificate_physical", "certificate_vs_physical", "A3/18 certificate vs physical", "rebar_a3_18_exact_date_bubble.csv", "date", "certificate_vs_physical_bubble_pct"),
    BubbleSeriesSpec("a3_12_certificate_physical", "certificate_vs_physical", "A3/12 sensitivity: certificate vs physical", "rebar_a3_12_exact_date_bubble.csv", "date", "certificate_vs_physical_bubble_pct"),
)


def build():
    return build_project_distributions(project_dir=PROJECT_DIR, commodity="rebar", specs=SPECS)


if __name__ == "__main__":
    result = build()
    print(f"Built {len(result)} rebar distribution rows")
