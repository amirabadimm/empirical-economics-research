"""Archive official CME metals bulletins and extract COMEX copper aggregate activity."""

from __future__ import annotations

import argparse
import csv
import io
import re
import time
from pathlib import Path

import requests
import truststore
import pdfplumber
from pypdf import PdfReader


PROJECT_DIR = Path(__file__).resolve().parents[3]
SOURCE_DIR = PROJECT_DIR / "data" / "raw" / "global_market" / "cme"
CDX_URL = "https://web.archive.org/cdx/search/cdx"
BULLETIN_URL = "www.cmegroup.com/daily_bulletin/current/Section62_Metals_Futures_Products.pdf"
CONTRACT_FIELDS = [
    "trade_date", "contract_month", "globex_open_usd_per_lb", "globex_high_usd_per_lb",
    "globex_low_usd_per_lb", "settlement_usd_per_lb", "settlement_change_usd_per_lb",
    "settlement_unchanged", "settlement_nominal", "globex_volume_contracts",
    "open_outcry_volume_contracts", "pnt_pit_volume_contracts", "open_interest_contracts",
    "open_interest_change_contracts",
    "archive_capture_utc", "original_source_url", "replay_url",
]


def capture_index(session: requests.Session, timeout: int) -> list[dict]:
    response = session.get(CDX_URL, params={
        "url": BULLETIN_URL,
        "output": "json",
        "filter": "statuscode:200",
        "fl": "timestamp,original,statuscode,mimetype,digest,length",
        "collapse": "digest",
    }, timeout=timeout)
    response.raise_for_status()
    document = response.json()
    return [dict(zip(document[0], row)) for row in document[1:]]


def parse_bulletin(payload: bytes) -> dict:
    text = "\n".join(page.extract_text() or "" for page in PdfReader(io.BytesIO(payload)).pages)
    date_match = re.search(r"PG62\s+\w{3},\s+([A-Z][a-z]{2} \d{1,2}, \d{4})", text)
    section_match = re.search(r"HG FUT COMEX COPPER FUTURES", text)
    if not date_match or not section_match:
        raise RuntimeError("missing bulletin date or HG FUT section")
    legacy_total_match = re.search(
        r"(\d+)TOTAL\s+HG FUT\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*([+-])", text
    )
    total_match = re.search(
        r"(\d+)TOTAL\s+HG FUT\s+(\d+)\s+(?:(\d+)\s+)?(\d+)([+-])", text
    )
    zero_volume_match = re.search(r"TOTAL\s+HG FUT\s+(\d+)\s+(\d+)([+-])", text)
    if legacy_total_match:
        globex_volume = int(legacy_total_match.group(1))
        open_outcry_volume = int(legacy_total_match.group(2))
        open_interest = int(legacy_total_match.group(3))
        pnt_pit_volume = int(legacy_total_match.group(4))
        change = int(legacy_total_match.group(5))
        sign = legacy_total_match.group(6)
    elif not total_match:
        if not zero_volume_match:
            raise RuntimeError("missing HG FUT aggregate volume/open-interest row")
        globex_volume, open_outcry_volume, pnt_pit_volume = 0, 0, 0
        open_interest = int(zero_volume_match.group(1))
        change = int(zero_volume_match.group(2))
        sign = zero_volume_match.group(3)
    else:
        globex_volume = int(total_match.group(1))
        open_outcry_volume = 0
        open_interest = int(total_match.group(2))
        pnt_pit_volume = int(total_match.group(3) or 0)
        change = int(total_match.group(4))
        sign = total_match.group(5)
    if sign == "-":
        change *= -1
    return {
        "trade_date": __import__("pandas").to_datetime(date_match.group(1)).date().isoformat(),
        "globex_volume_contracts": globex_volume,
        "open_outcry_volume_contracts": open_outcry_volume,
        "pnt_pit_volume_contracts": pnt_pit_volume,
        "futures_volume_contracts": globex_volume + open_outcry_volume + pnt_pit_volume,
        "open_interest_contracts": open_interest,
        "open_interest_change_contracts": change,
    }


def _number(text: str, integer: bool = False) -> float | int | None:
    value = text.strip().replace(",", "").replace("/", "")
    value = re.sub(r"[ABNP]$", "", value)
    if value in {"", "----", "--"}:
        return None
    match = re.search(r"[-+]?\d+" if integer else r"[-+]?\d+(?:\.\d+)?", value)
    if not match:
        return None
    return int(match.group()) if integer else float(match.group())


def _line_groups(words: list[dict]) -> list[list[dict]]:
    groups: list[list[dict]] = []
    for word in sorted(words, key=lambda item: (item["top"], item["x0"])):
        if not groups or abs(groups[-1][0]["top"] - word["top"]) > 1.0:
            groups.append([word])
        else:
            groups[-1].append(word)
    return [sorted(group, key=lambda item: item["x0"]) for group in groups]


def _bin_text(words: list[dict], lower: float, upper: float) -> str:
    return "".join(word["text"] for word in words if lower <= word["x0"] < upper)


def parse_contract_prices(payload: bytes, trade_date: str) -> list[dict]:
    """Parse HG contract rows using PDF coordinates, not flattened-text spacing."""
    rows: list[dict] = []
    with pdfplumber.open(io.BytesIO(payload)) as document:
        legacy_layout = "OPEN OUTCRY" in "\n".join(page.extract_text() or "" for page in document.pages)
        in_hg = False
        for page in document.pages:
            for words in _line_groups(page.extract_words()):
                line = " ".join(word["text"] for word in words)
                if line.startswith("HG FUT COMEX COPPER FUTURES"):
                    in_hg = True
                    continue
                if not in_hg:
                    continue
                if line.startswith("TOTAL HG FUT"):
                    in_hg = False
                    continue
                contract = words[0]["text"] if words else ""
                if not re.fullmatch(r"[A-Z]{3}\d{2}", contract):
                    continue
                open_text = _bin_text(words, 35, 75) if legacy_layout else _bin_text(words, 110, 180)
                high_low_text = "".join(
                    word["text"] for word in words
                    if ((125 <= word["x0"] < 195) if legacy_layout
                        else (180 <= word["x0"] < 270))
                )
                high_low = re.findall(r"\d+(?:\.\d+)?", high_low_text)
                high_text = high_low[0] if high_low else ""
                low_text = high_low[1] if len(high_low) > 1 else ""
                settlement_text = (
                    _bin_text(words, 350, 387) if legacy_layout else _bin_text(words, 270, 315)
                )
                change_words = [
                    word["text"] for word in words
                    if ((387 <= word["x0"] < 430) if legacy_layout
                        else (315 <= word["x0"] < 400))
                ]
                change_text = "".join(change_words)
                unchanged = "UNCH" in change_text
                change = 0.0 if unchanged else _number(change_text.replace("+", ""))
                if change is not None and change_text.startswith("-"):
                    change = -abs(float(change))
                rows.append({
                    "trade_date": trade_date,
                    "contract_month": contract,
                    "globex_open_usd_per_lb": _number(open_text),
                    "globex_high_usd_per_lb": _number(high_text),
                    "globex_low_usd_per_lb": _number(low_text),
                    "settlement_usd_per_lb": _number(settlement_text),
                    "settlement_change_usd_per_lb": change,
                    "settlement_unchanged": unchanged,
                    "settlement_nominal": settlement_text.endswith("N"),
                    "globex_volume_contracts": _number(
                        _bin_text(words, 460, 504) if legacy_layout else _bin_text(words, 400, 470),
                        integer=True,
                    ),
                    "open_outcry_volume_contracts": _number(
                        _bin_text(words, 425, 460), integer=True
                    ) if legacy_layout else None,
                    "pnt_pit_volume_contracts": _number(
                        _bin_text(words, 500, 530) if legacy_layout else _bin_text(words, 470, 530),
                        integer=True,
                    ),
                    "open_interest_contracts": _number(
                        _bin_text(words, 530, 558) if legacy_layout else _bin_text(words, 530, 562),
                        integer=True,
                    ),
                    "open_interest_change_contracts": _signed_integer(
                        words, 558 if legacy_layout else 562
                    ),
                })
    if not rows:
        raise RuntimeError("missing coordinate-parsed HG contract rows")
    return rows


def _signed_integer(words: list[dict], lower: float) -> int | None:
    text = "".join(word["text"] for word in words if word["x0"] >= lower)
    if "UNCH" in text:
        return 0
    sign = -1 if text.startswith("-") else 1
    value = _number(text.lstrip("+-"), integer=True)
    return None if value is None else sign * int(value)


def download(session: requests.Session, url: str, timeout: int) -> bytes:
    last_error: Exception | None = None
    for attempt in range(5):
        try:
            response = session.get(url, timeout=timeout)
            response.raise_for_status()
            if not response.content.startswith(b"%PDF"):
                raise RuntimeError("response is not PDF")
            return response.content
        except (requests.RequestException, RuntimeError) as error:
            last_error = error
            if attempt < 4:
                time.sleep(2 ** attempt)
    raise RuntimeError(f"failed to download {url}") from last_error


def collect(timeout: int, delay: float) -> tuple[Path, int]:
    truststore.inject_into_ssl()
    session = requests.Session()
    session.headers["User-Agent"] = "Mozilla/5.0 empirical-economics-research"
    SOURCE_DIR.mkdir(parents=True, exist_ok=True)
    snapshots = SOURCE_DIR / "bulletin_snapshots"
    snapshots.mkdir(exist_ok=True)
    captures = capture_index(session, timeout)
    manifest_rows: list[dict] = []
    observations: list[dict] = []
    contracts: list[dict] = []
    for index, capture in enumerate(captures, start=1):
        timestamp = capture["timestamp"]
        replay_url = f"https://web.archive.org/web/{timestamp}id_/{capture['original']}"
        snapshot = snapshots / f"cme_metals_bulletin_{timestamp}.pdf"
        payload = snapshot.read_bytes() if snapshot.exists() else download(session, replay_url, timeout)
        if not snapshot.exists():
            with snapshot.open("xb") as handle:
                handle.write(payload)
            time.sleep(delay)
        error = ""
        try:
            row = parse_bulletin(payload) | {
                "archive_capture_utc": timestamp,
                "original_source_url": capture["original"],
                "replay_url": replay_url,
            }
            observations.append(row)
            contracts.extend(
                contract | {
                    "archive_capture_utc": timestamp,
                    "original_source_url": capture["original"],
                    "replay_url": replay_url,
                }
                for contract in parse_contract_prices(payload, row["trade_date"])
            )
        except Exception as exc:
            error = f"{type(exc).__name__}: {exc}"
        manifest_rows.append(capture | {"replay_url": replay_url, "snapshot": snapshot.name, "parse_error": error})
        if index % 20 == 0:
            print(f"cme bulletins: processed {index}/{len(captures)} captures", flush=True)
    manifest = SOURCE_DIR / "cme_metals_bulletin_capture_manifest.csv"
    with manifest.with_suffix(".csv.tmp").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(manifest_rows[0]))
        writer.writeheader()
        writer.writerows(manifest_rows)
    manifest.with_suffix(".csv.tmp").replace(manifest)
    errors = [row for row in manifest_rows if row["parse_error"]]
    if errors:
        raise RuntimeError(f"{len(errors)} CME bulletins failed parsing; see {manifest}")
    latest = {}
    for row in observations:
        if row["trade_date"] not in latest or row["archive_capture_utc"] > latest[row["trade_date"]]["archive_capture_utc"]:
            latest[row["trade_date"]] = row
    rows = sorted(latest.values(), key=lambda row: row["trade_date"])
    output = SOURCE_DIR / "comex_copper_daily_activity_raw.csv"
    with output.with_suffix(".csv.tmp").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    output.with_suffix(".csv.tmp").replace(output)
    latest_contracts = {}
    for row in contracts:
        key = (row["trade_date"], row["contract_month"])
        if key not in latest_contracts or row["archive_capture_utc"] > latest_contracts[key]["archive_capture_utc"]:
            latest_contracts[key] = row
    contract_rows = sorted(latest_contracts.values(), key=lambda row: (row["trade_date"], row["contract_month"]))
    contract_output = SOURCE_DIR / "comex_copper_contract_prices_raw.csv"
    with contract_output.with_suffix(".csv.tmp").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CONTRACT_FIELDS)
        writer.writeheader()
        writer.writerows(contract_rows)
    contract_output.with_suffix(".csv.tmp").replace(contract_output)
    print(f"cme bulletins: {len(captures)} official PDFs; {len(rows)} unique trade dates")
    print(f"cme contract prices: {len(contract_rows)} contract-date rows -> {contract_output}")
    return output, len(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=120)
    parser.add_argument("--delay", type=float, default=0.15)
    args = parser.parse_args()
    path, count = collect(args.timeout, args.delay)
    print(f"cme bulletins: {count:,} rows -> {path}")


if __name__ == "__main__":
    main()
