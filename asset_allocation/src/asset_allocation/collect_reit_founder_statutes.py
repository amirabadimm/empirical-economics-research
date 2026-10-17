"""Archive the two signed fund statutes that explicitly list legal founders."""
from __future__ import annotations

import hashlib

import requests

from asset_allocation.build_reit_assembly_reinvestment import ROOT
from asset_allocation.collect_reit_instrument_info import atomic_bytes

SOURCES = {
    "67717913151786055": "https://nikrayreits.ir/Download/DownloadPDFByAttachmentId?attachmentId=547",
    "34322849244939912": "https://kashane.pgibc.ir/Download/DownloadPDFByAttachmentId?attachmentId=523",
}
SNAPSHOTS = ROOT / "data/raw/real_estate_funds/founder_statute_snapshots"


def collect() -> list[str]:
    result = []
    for code, url in SOURCES.items():
        response = requests.get(url, timeout=45)
        response.raise_for_status()
        body = response.content
        if not body.startswith(b"%PDF-"):
            raise ValueError(f"Fund statute is not a PDF: {code}")
        digest = hashlib.sha256(body).hexdigest()
        path = SNAPSHOTS / f"{code}_{digest}.pdf"
        if path.exists():
            if path.read_bytes() != body:
                raise ValueError(f"Corrupt statute snapshot: {path}")
        else:
            atomic_bytes(path, body)
        result.append(path.relative_to(ROOT).as_posix())
    return result


if __name__ == "__main__":
    print("\n".join(collect()))
