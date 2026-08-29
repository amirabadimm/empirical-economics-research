"""Build Copper report figures from canonical processed CSV files."""

from pathlib import Path
import sys


WORKSPACE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(WORKSPACE / "reports" / "shared"))

from bubble_report_figures import build  # noqa: E402


if __name__ == "__main__":
    build(
        processed=WORKSPACE / "commodity" / "copper" / "data" / "processed" / "bubble",
        output=Path(__file__).resolve().parent / "figures",
        commodity="copper",
        main_filename="copper_certificate_bubble.csv",
    )
