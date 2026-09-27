"""Build the distribution of the existing bitumen comparison."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
sys.path.insert(0, str(ROOT))
from shared.market_analysis.bubble_distribution import BubbleSeriesSpec, build_project_distributions

if __name__ == "__main__":
    build_project_distributions(
        project_dir=Path(__file__).resolve().parents[3], commodity="bitumen",
        specs=(BubbleSeriesSpec("certificate_physical", "certificate_vs_physical",
            "Domestic 60/70 cash diagnostic", "bitumen_certificate_bubble.csv",
            "date", "premium_discount_pct", point_method_column="physical_price_method"),),
    )
