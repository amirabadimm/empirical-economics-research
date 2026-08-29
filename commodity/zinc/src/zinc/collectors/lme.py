"""Zinc configuration for the shared Westmetall/LME collector."""

import argparse
import sys
from pathlib import Path

WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))
from shared.market_data.lme import (  # noqa: E402
    OUTPUT_COLUMNS,
    LmeConfig,
    build_url as _build_url,
    collect,
    parse_page as _parse_page,
    read_existing,
    write_atomic as write_csv_atomic,
)

CONFIG = LmeConfig("zinc", "LME_Zn_cash", "zinc_lme_raw.csv")


def build_url(year: int) -> str:
    return _build_url(CONFIG, year)


def parse_page(html: bytes, year: int, fetched_at: str, url: str) -> list[dict[str, str]]:
    return _parse_page(html, CONFIG, year, fetched_at, url)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=30)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--delay", type=float, default=1.0)
    args = parser.parse_args()
    collect(Path(__file__).resolve().parents[3], CONFIG, args.timeout, args.retries, args.delay)


if __name__ == "__main__":
    main()
