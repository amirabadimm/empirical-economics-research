from __future__ import annotations

import json
from pathlib import Path

from .common import ROOT, read_archive


def verify(root: Path = ROOT) -> dict:
    processed = root / "data/processed"
    paths = set()
    discovery = json.loads((processed / "discovery_raw_manifest.json").read_text(encoding="utf-8"))
    paths.update(item["archive"] for item in discovery["search"])
    paths.update(item["archive"] for item in discovery["identity"])
    paths.add(discovery["market_watch"])
    availability = json.loads((processed / "availability_audit.json").read_text(encoding="utf-8"))
    paths.update(availability["archives"].values())
    downloads = json.loads((processed / "download_manifest.json").read_text(encoding="utf-8"))
    paths.update(item["archive"] for item in downloads.values())
    audit = json.loads((processed / "download_audit.json").read_text(encoding="utf-8"))
    paths.update(item["archive"] for item in audit["failures"] if item.get("archive"))
    probe = json.loads((processed / "period_probe.json").read_text(encoding="utf-8"))
    paths.update(item["archive"] for item in probe["results"] if item.get("archive"))
    for relative in paths:
        path = (root / relative).resolve()
        if not path.is_relative_to((root / "data/raw").resolve()):
            raise ValueError(f"Archive pointer outside raw directory: {relative}")
        read_archive(path)
    return {"verified_archives": len(paths), "hash_mismatches": 0}
