"""Archive dated TSETMC supervisor notices for the eight REITs, unchanged by builders."""
from __future__ import annotations

import hashlib
import json
from datetime import date

import requests

from asset_allocation.build_reit_assembly_reinvestment import FUNDS, ROOT
from asset_allocation.collect_reit_instrument_info import atomic_bytes

BASE = "https://cdn.tsetmc.com/api/Msg/GetMsgByInsCode/"
SNAPSHOTS = ROOT / "data/raw/real_estate_funds/subscription_notice_snapshots"


def collect() -> list[str]:
    paths = []
    session = requests.Session()
    for code in FUNDS:
        response = session.get(BASE + code, timeout=25)
        response.raise_for_status()
        payload = response.json()
        if not isinstance(payload, dict) or not isinstance(payload.get("msg"), list):
            raise ValueError(f"Unexpected TSETMC notice response for {code}")
        body = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        digest = hashlib.sha256(body).hexdigest()
        path = SNAPSHOTS / f"{code}_{date.today():%Y%m%d}_{digest}.json"
        if path.exists():
            if path.read_bytes() != body:
                raise ValueError(f"Corrupt notice snapshot: {path}")
        else:
            atomic_bytes(path, body)
        paths.append(path.relative_to(ROOT).as_posix())
    return paths


if __name__ == "__main__":
    print("\n".join(collect()))
