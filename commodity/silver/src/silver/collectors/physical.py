"""Collect broad silver-related rows from complete official IME responses."""
from __future__ import annotations
import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[5]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from shared.ime_data.ime_physical_collector import (  # noqa: E402
    PhysicalCollectorConfig, collect, normalize_fa, rebuild_from_snapshots,
)

def is_silver_related(row: dict) -> bool:
    return "نقره" in normalize_fa(row.get("GoodsName"))

def config(project_dir: Path | None = None) -> PhysicalCollectorConfig:
    return PhysicalCollectorConfig(
        project_dir=project_dir or Path(__file__).resolve().parents[3],
        output_filename="silver_physical_raw.csv", snapshot_prefix="physical",
        target_label="silver-related", row_filter=is_silver_related,
    )

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--refresh-months", type=int, default=2)
    parser.add_argument("--start-month")
    parser.add_argument("--end-month")
    parser.add_argument("--rebuild-from-snapshots", action="store_true")
    args = parser.parse_args()
    if args.rebuild_from_snapshots:
        rebuild_from_snapshots(config())
    else:
        collect(config(), args.timeout, args.retries, args.refresh_months,
                args.start_month, args.end_month)

if __name__ == "__main__":
    main()
