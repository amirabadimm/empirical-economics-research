"""Archive exchange adjusted-price histories and validate against raw fund closes."""

from __future__ import annotations

import csv
import hashlib
import os
import tempfile
from datetime import datetime
from pathlib import Path

import pandas as pd
import requests

from asset_allocation.collectors.tsetmc_reits import MANIFEST, RAW

ROOT = Path(__file__).resolve().parents[3]
SNAPSHOTS = RAW / "adjusted_price_snapshots"
OUTPUT = ROOT / "data/processed/analysis/reit_adjusted_daily.csv"
URL = "https://members.tsetmc.com/tsev2/chart/data/Financial.aspx"


def archive(payload: bytes) -> Path:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOTS / (hashlib.sha256(payload).hexdigest() + ".txt")
    if not path.exists():
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=SNAPSHOTS, suffix=".tmp") as file:
            file.write(payload)
            temporary = Path(file.name)
        os.replace(temporary, path)
    return path


def parse_chart(payload: bytes) -> dict[str, float]:
    rows = {}
    for record in payload.decode("utf-8-sig").strip().strip(";").split(";"):
        values = record.split(",")
        if len(values) != 7:
            raise ValueError(f"Invalid exchange chart record: {record[:80]}")
        day = datetime.strptime(values[0], "%Y%m%d").date().isoformat()
        close = float(values[-1])
        if close <= 0 or day in rows:
            raise ValueError(f"Invalid or duplicate adjusted close on {day}")
        rows[day] = close
    if not rows:
        raise ValueError("Empty exchange price chart")
    return rows


def request_chart(code: str, adjusted: bool) -> bytes:
    response = requests.get(URL, params={"i": code, "t": "ph", "a": int(adjusted)},
                            headers={"User-Agent": "asset-allocation-research/0.1"}, timeout=60)
    response.raise_for_status()
    return response.content


def collect() -> pd.DataFrame:
    with MANIFEST.open(encoding="utf-8", newline="") as file:
        instruments = list(csv.DictReader(file))
    output = []
    for instrument in instruments:
        code = instrument["ins_code"]
        raw_payload = request_chart(code, False)
        adjusted_payload = request_chart(code, True)
        unadjusted, adjusted = parse_chart(raw_payload), parse_chart(adjusted_payload)
        if set(unadjusted) != set(adjusted):
            raise ValueError(f"Exchange chart dates differ for {code}")
        with (RAW / f"{code}.csv").open(encoding="utf-8", newline="") as file:
            canonical = {row["source_date_gregorian"]: float(row["closing_price_irr"])
                         for row in csv.DictReader(file) if row["has_trade"] == "true"}
        overlap = set(canonical) & set(unadjusted)
        if len(overlap) < max(3, int(0.9 * len(unadjusted))):
            raise ValueError(f"Insufficient unadjusted price overlap for {code}")
        if any(abs(canonical[day] - unadjusted[day]) > 0.5 for day in overlap):
            raise ValueError(f"Exchange unadjusted chart conflicts with canonical close for {code}")
        raw_snapshot = archive(raw_payload)
        adjusted_snapshot = archive(adjusted_payload)
        for day in sorted(adjusted):
            output.append({"source_date_gregorian": day, "ins_code": code,
                           "unadjusted_close_irr": unadjusted[day],
                           "adjusted_close_irr": adjusted[day],
                           "adjustment_factor": adjusted[day] / unadjusted[day],
                           "raw_snapshot": str(raw_snapshot.relative_to(ROOT)),
                           "adjusted_snapshot": str(adjusted_snapshot.relative_to(ROOT))})
    frame = pd.DataFrame(output)
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False,
                                     dir=OUTPUT.parent, suffix=".tmp") as file:
        frame.to_csv(file, index=False)
        temporary = Path(file.name)
    os.replace(temporary, OUTPUT)
    return frame


if __name__ == "__main__":
    frame = collect()
    print(f"Validated and archived {len(frame)} exchange adjusted-price observations for {frame.ins_code.nunique()} funds")
