"""Collect the approved copper-cathode physical-market raw scope.

The canonical raw table keeps the old/new National Iranian Copper Industries
symbols, cash and cash-matching contracts, and zero-quantity offers. Complete
monthly IME responses are archived before this project-specific filter runs.
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
    gregorian_to_jalali,
    jalali_to_gregorian,
    normalize_fa,
    rebuild_from_snapshots,
)


TARGET_SYMBOLS = {"NCI-CCAA-00", "NCI-OACCAA-00"}
TARGET_CONTRACTS = {"نقدی", "نقدی (مچینگ)"}


def is_approved_copper_cathode(row: dict) -> bool:
    return (
        normalize_fa(row.get("GoodsName")) == "مس کاتد"
        and str(row.get("Symbol") or "").strip() in TARGET_SYMBOLS
        and normalize_fa(row.get("ContractType")) in TARGET_CONTRACTS
    )


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
        output_filename="copper_cathode_physical_raw.csv",
        snapshot_prefix="physical",
        target_label="approved NCI copper cathode",
        row_filter=is_approved_copper_cathode,
    )
    if args.rebuild_from_snapshots:
        rebuild_from_snapshots(config)
    else:
        collect(
            config,
            args.timeout,
            args.retries,
            args.refresh_months,
            args.start_month,
            args.end_month,
        )


if __name__ == "__main__":
    main()
