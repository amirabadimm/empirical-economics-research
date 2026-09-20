from __future__ import annotations

import csv
import json
from pathlib import Path
from urllib.parse import quote

from .common import ROOT, archive_json, atomic_bytes, fetch_json, session
from .discover_contracts import BASE


def refresh(root: Path = ROOT, *, delay: float = 0.15) -> dict:
    audit = json.loads((root / "data/processed/discovery_audit.json").read_text(encoding="utf-8"))
    with (root / "data/processed/ahrom_option_contracts.csv").open(encoding="utf-8-sig", newline="") as source:
        contracts = list(csv.DictReader(source))
    client = session()
    refreshed = {"search": [], "identity": [], "market_watch": None, "failures": []}
    for record in audit["search_queries"]:
        query = record["query"]
        try:
            body = fetch_json(client, BASE + "GetInstrumentSearch/" + quote(query), delay=delay)
            path = archive_json(root / "data/raw/tsetmc/search", body)
            refreshed["search"].append({"query": query, "archive": str(path.relative_to(root))})
        except Exception as exc:
            refreshed["failures"].append({"source": "search", "query": query,
                                           "error": type(exc).__name__})
    body = fetch_json(client, BASE + "GetInstrumentOptionMarketWatch/1", delay=delay)
    path = archive_json(root / "data/raw/tsetmc/market_watch", body)
    refreshed["market_watch"] = str(path.relative_to(root))
    for index, contract in enumerate(contracts, 1):
        code = contract["ins_code"]
        try:
            body = fetch_json(client, BASE + "GetInstrumentIdentity/" + code, delay=delay)
            path = archive_json(root / "data/raw/tsetmc/identity" / code, body)
            refreshed["identity"].append({"ins_code": code, "archive": str(path.relative_to(root))})
        except Exception as exc:
            refreshed["failures"].append({"source": "identity", "ins_code": code,
                                           "error": type(exc).__name__})
        if index % 50 == 0:
            print(f"TSETMC discovery sources recaptured: {index}/{len(contracts)}", flush=True)
    atomic_bytes(root / "data/processed/discovery_raw_manifest.json",
                 json.dumps(refreshed, ensure_ascii=False, indent=2).encode())
    return {"search": len(refreshed["search"]), "identity": len(refreshed["identity"]),
            "failures": len(refreshed["failures"])}
