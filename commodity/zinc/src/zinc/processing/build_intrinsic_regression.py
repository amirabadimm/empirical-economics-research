"""Run the shared intrinsic-value regression for Zinc."""

import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
from shared.market_analysis.intrinsic_regression import build  # noqa: E402


def main() -> None:
    output, metrics = build(Path(__file__).resolve().parents[3])
    selected = metrics.loc[metrics["selected"].eq(1), "model"].iloc[0]
    print(f"Selected model: {selected}")
    print(f"Rows: {len(output)}; anchors: {output['is_actual_physical_observation'].sum()}")


if __name__ == "__main__":
    main()
