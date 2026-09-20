from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from ahrom_options.build_dataset import build  # noqa: E402
from ahrom_options.availability import enrich  # noqa: E402
from ahrom_options.common import ROOT  # noqa: E402
from ahrom_options.discover_contracts import discover  # noqa: E402
from ahrom_options.optionbaaz_client import collect  # noqa: E402
from ahrom_options.refresh_discovery_archive import refresh  # noqa: E402
from ahrom_options.probe_periods import probe  # noqa: E402
from ahrom_options.verify_archives import verify  # noqa: E402


def load_contracts() -> list[dict]:
    with (ROOT / "data/processed/ahrom_option_contracts.csv").open(encoding="utf-8-sig", newline="") as source:
        return list(csv.DictReader(source))


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect Ahrom option history")
    parser.add_argument("stage", choices=("discover", "availability", "collect", "build",
                                          "refresh-discovery-archive", "probe-periods", "verify", "all"))
    parser.add_argument("--refresh", action="store_true", help="Capture a new immutable OptionBaaz version")
    parser.add_argument("--limit", type=int, help="Limit contract requests during a trial")
    parser.add_argument("--delay", type=float, default=0.35, help="Seconds between requests")
    args = parser.parse_args()
    contracts = None
    if args.stage in ("discover", "all"):
        contracts = discover(delay=args.delay)
        print(f"Verified TSETMC contracts: {len(contracts)}", flush=True)
    if args.stage in ("availability", "all"):
        result = enrich(delay=args.delay, refresh=args.refresh)
        print(json.dumps({key: value for key, value in result.items()
                          if key not in ("archives", "failures")}, ensure_ascii=True, indent=2), flush=True)
        contracts = load_contracts()
    if args.stage in ("collect", "all"):
        contracts = contracts if contracts is not None else load_contracts()
        result = collect(contracts[:args.limit] if args.limit else contracts,
                         refresh=args.refresh, delay=args.delay)
        print(json.dumps({key: value for key, value in result.items()
                          if key not in ("failures", "validation_errors")},
                         ensure_ascii=True, indent=2), flush=True)
    if args.stage in ("build", "all"):
        print(json.dumps(build(), ensure_ascii=True, indent=2), flush=True)
    if args.stage == "refresh-discovery-archive":
        print(json.dumps(refresh(delay=args.delay), ensure_ascii=True, indent=2), flush=True)
    if args.stage == "probe-periods":
        print(json.dumps([{key: value for key, value in row.items() if key != "archive"}
                          for row in probe(delay=args.delay)], ensure_ascii=True, indent=2), flush=True)
    if args.stage == "verify":
        print(json.dumps(verify(), ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
