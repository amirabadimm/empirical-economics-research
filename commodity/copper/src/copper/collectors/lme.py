"""Copper configuration for the shared Westmetall/LME collector."""

import argparse
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
from shared.market_data.lme import LmeConfig, collect  # noqa: E402

CONFIG = LmeConfig("copper", "LME_Cu_cash", "copper_lme_raw.csv")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()
    collect(Path(__file__).resolve().parents[3], CONFIG, args.timeout, args.retries, args.delay)


if __name__ == "__main__":
    main()
