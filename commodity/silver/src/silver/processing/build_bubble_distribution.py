"""Build the observed silver bubble distribution."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from shared.market_analysis.bubble_distribution import BubbleSeriesSpec, build_project_distributions  # noqa: E402

def main() -> None:
    project = Path(__file__).resolve().parents[3]
    build_project_distributions(project_dir=project, commodity="silver", specs=(
        BubbleSeriesSpec("silver_certificate_physical", "certificate_vs_physical",
                         "999.9 silver certificate vs same-date IME cash bar",
                         "silver_certificate_physical.csv", "date", "premium_discount_pct",
                         point_method_column="alignment_method"),
    ))

if __name__ == "__main__":
    main()
