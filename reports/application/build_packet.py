"""Build a local reader packet from an explicit report/figure allowlist.

The packet contains no datasets, notebooks, secrets, or bulk repository archive.
Links to files outside this reader packet become labelled repository references.
Run the evidence verifier before preparing a packet for a different checkpoint.
"""

from __future__ import annotations

import hashlib
import json
import posixpath
import re
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile, ZipInfo

from verify_claims import REPORT, ROOT, render, require


FILES = {
    "reports/application/README.md": "PORTFOLIO.md",
    "reports/application/CV_PROJECTS.md": "CV_PROJECTS.md",
    "reports/application/EVIDENCE.md": "EVIDENCE.md",
    "reports/application/HANDOFF.md": "HANDOFF.md",
    "reports/copper/research/REPORT.md": "research/copper.md",
    "reports/zinc/research/REPORT.md": "research/zinc.md",
    "commodity/gold/reports/RESEARCH_SUMMARY.md": "research/gold.md",
    "asset_allocation/reports/CURRENT_RESEARCH_SUMMARY.md": "research/allocation.md",
    "LICENSE": "LICENSE",
    "DATA_AVAILABILITY.md": "DATA_AVAILABILITY.md",
}
for commodity in ("copper", "zinc"):
    for kind in ("main", "certificate", "physical"):
        name = f"{commodity}_{kind}_bubble.png"
        FILES[f"reports/{commodity}/research/figures/{name}"] = f"research/figures/{name}"


def localize(text: str, source: str, destination: str) -> str:
    def replace(match: re.Match) -> str:
        label, target = match.groups()
        if "://" in target or target.startswith(("#", "mailto:")):
            return match.group(0)
        path, separator, fragment = target.partition("#")
        resolved = posixpath.normpath(posixpath.join(posixpath.dirname(source), path))
        if resolved in FILES:
            local = posixpath.relpath(FILES[resolved], posixpath.dirname(destination) or ".")
            return f"[{label}]({local}{separator}{fragment})"
        return f"{label} (repository file: `{resolved}`)"

    return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, text)


def build() -> Path:
    require(REPORT.read_text(encoding="utf-8") == render(), "Run evidence review before packaging: checkpoint changed")
    payloads: dict[str, bytes] = {}
    manifest = []
    for source, destination in FILES.items():
        original = (ROOT / source).read_bytes()
        content = localize(original.decode("utf-8"), source, destination).encode("utf-8") if source.endswith(".md") else original
        payloads[destination] = content
        manifest.append({
            "source": source, "packet_path": destination,
            "source_sha256": hashlib.sha256(original).hexdigest(),
            "packet_sha256": hashlib.sha256(content).hexdigest(),
        })
    payloads["START_HERE.md"] = (
        "# Economics application reader packet\n\n"
        "Mohammad Mahdi Amirabadi · Closed portfolio edition: 2026-10-25\n\n"
        "Start with [the portfolio](PORTFOLIO.md) and [CV project descriptions](CV_PROJECTS.md).\n"
        "The research folder contains copper, zinc, gold, and allocation summaries.\n"
        "[Evidence](EVIDENCE.md) documents the numerical claims.\n\n"
        "[Handoff](HANDOFF.md) is a personal maintenance companion; it records remaining\n"
        "work and does not form part of the CV text. Add your verified project dates\n"
        "and institutional affiliation before placing the project entries in your CV.\n\n"
        "This is a reader packet of original summaries and selected figures, not a full\n"
        "research environment or data release. References marked 'repository file'\n"
        "require the accompanying repository checkout. No raw or processed datasets\n"
        "are included. The materials preserve the final documented research scope;\n"
        "remote services and source-data backups are outside this packet.\n\n"
        "MANIFEST.json fingerprints the source documents and packaged copies.\n"
    ).encode("utf-8")
    payloads["MANIFEST.json"] = (json.dumps(manifest, indent=2) + "\n").encode("utf-8")
    for name, content in payloads.items():
        if not name.endswith(".md"):
            continue
        for target in re.findall(r"\]\(([^)]+)\)", content.decode("utf-8")):
            if "://" in target or target.startswith(("#", "mailto:")):
                continue
            resolved = posixpath.normpath(posixpath.join(posixpath.dirname(name), target.split("#")[0]))
            require(resolved in payloads, f"Broken packet link: {name} -> {target}")
    output = Path(__file__).parent / "outputs" / "economics_application_2026-10-25.zip"
    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_suffix(".zip.tmp")
    with ZipFile(temporary, "w", compression=ZIP_DEFLATED) as archive:
        for name, content in sorted(payloads.items()):
            info = ZipInfo(name, date_time=(2026, 10, 25, 0, 0, 0))
            info.compress_type = ZIP_DEFLATED
            archive.writestr(info, content)
    with ZipFile(temporary) as archive:
        require(archive.testzip() is None, "ZIP integrity check failed")
        require(set(archive.namelist()) == set(payloads), "Unexpected ZIP contents")
        for name, content in payloads.items():
            require(archive.read(name) == content, f"Packet bytes mismatch: {name}")
    temporary.replace(output)
    print(f"Verified reader packet: {output} ({len(payloads)} files; {output.stat().st_size:,} bytes)")
    return output


if __name__ == "__main__":
    build()
