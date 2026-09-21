"""Build the standardized empirical pellet bubble distribution."""

import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.market_analysis.bubble_distribution import BubbleSeriesSpec, build_project_distributions


PROJECT_DIR = Path(__file__).resolve().parents[3]
SPECS = (
    BubbleSeriesSpec("certificate_physical", "certificate_vs_physical", "Certificate vs physical", "pellet_certificate_bubble.csv", "date", "bubble_pct"),
)


def build():
    return build_project_distributions(project_dir=PROJECT_DIR, commodity="pellet", specs=SPECS)


if __name__ == "__main__":
    result = build()
    print(f"Built {len(result)} pellet distribution rows")
