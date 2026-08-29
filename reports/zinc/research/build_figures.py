"""Build Zinc report figures from canonical processed CSV files."""

from pathlib import Path
import sys


WORKSPACE = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(WORKSPACE / "reports" / "shared"))

from bubble_report_figures import build  # noqa: E402


if __name__ == "__main__":
    build(
        processed=WORKSPACE / "commodity" / "zinc" / "data" / "processed" / "bubble",
        output=Path(__file__).resolve().parent / "figures",
        commodity="zinc",
        main_filename="zinc_certificate_bubble.csv",
    )
