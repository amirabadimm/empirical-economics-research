"""Collect every bitumen-related physical-market row from the official IME API.

This broad raw collector deliberately keeps every row whose normalized
GoodsName contains «قیر»: all grades, producers, symbols, contract and
settlement types, including zero-quantity offers. Underlying selection is a
later, explicitly approved processing step.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


WORKSPACE_ROOT = Path(__file__).resolve().parents[5]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from shared.ime_data.ime_physical_collector import (  # noqa: E402
    PhysicalCollectorConfig,
    collect,
    normalize_fa,
    rebuild_from_snapshots,
)


def is_bitumen(row: dict) -> bool:
    return "قیر" in normalize_fa(row.get("GoodsName"))


def main() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--refresh-months", type=int, default=2)
    parser.add_argument("--start-month", help="optional Jalali YYYY/MM override")
    parser.add_argument("--end-month", help="optional Jalali YYYY/MM override")
    parser.add_argument("--rebuild-from-snapshots", action="store_true")
    args = parser.parse_args()
    config = PhysicalCollectorConfig(
        project_dir=Path(__file__).resolve().parents[3],
        output_filename="bitumen_physical_raw.csv",
        snapshot_prefix="physical",
        target_label="bitumen",
        row_filter=is_bitumen,
    )
    if args.rebuild_from_snapshots:
        rebuild_from_snapshots(config)
    else:
        collect(config, args.timeout, args.retries, args.refresh_months,
                args.start_month, args.end_month)


if __name__ == "__main__":
    main()
