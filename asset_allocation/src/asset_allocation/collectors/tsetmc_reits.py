"""Discover and collect TSETMC real-estate investment fund trading history."""

from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
import unicodedata
from datetime import datetime
from pathlib import Path

import requests

ROOT = Path(__file__).resolve().parents[3]
RAW = ROOT / "data/raw/real_estate_funds"
SNAPSHOTS = RAW / "snapshots"
MANIFEST = RAW / "instruments.csv"
SEARCH = "https://cdn.tsetmc.com/api/Instrument/GetInstrumentSearch/"
HISTORY = "https://cdn.tsetmc.com/api/ClosingPrice/GetClosingPriceDailyList/{}/0"
TICKERS = ("کلید", "ارزش مسکن", "دانیک", "کاخ", "عمارت دی", "امین شهر", "مالک آتیه", "کاشانه")
FIELDS = ("source_date_gregorian", "ins_code", "ticker", "closing_price_irr", "trade_count", "trade_volume", "has_trade")


def normalized(value: str) -> str:
    value = unicodedata.normalize("NFKC", value).replace("ي", "ی").replace("ك", "ک")
    return "".join(ch for ch in value if ch.isalnum())


def atomic_csv(path: Path, fields: tuple[str, ...], rows: list[dict]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", newline="", delete=False, dir=path.parent, suffix=".tmp") as file:
        writer = csv.DictWriter(file, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
        temporary = Path(file.name)
    os.replace(temporary, path)


def archive(payload: bytes) -> Path:
    SNAPSHOTS.mkdir(parents=True, exist_ok=True)
    path = SNAPSHOTS / (hashlib.sha256(payload).hexdigest() + ".json")
    if not path.exists():
        with tempfile.NamedTemporaryFile("wb", delete=False, dir=SNAPSHOTS, suffix=".tmp") as file:
            file.write(payload)
            temporary = Path(file.name)
        os.replace(temporary, path)
    return path


def fetch(url: str) -> bytes:
    response = requests.get(url, headers={"User-Agent": "asset-allocation-research/0.1"}, timeout=60)
    response.raise_for_status()
    return response.content


def discover(ticker: str) -> dict[str, str]:
    from urllib.parse import quote
    payload = fetch(SEARCH + quote(ticker))
    entries = json.loads(payload)["instrumentSearch"]
    matches = [x for x in entries if normalized(x["lVal18AFC"]) == normalized(ticker)
               and "املاک" in normalized(x["lVal30"])]
    codes = {str(x["insCode"]) for x in matches}
    if len(codes) != 1:
        raise ValueError(f"Expected one real-estate instrument for {ticker}: {sorted(codes)}")
    entry = matches[0]
    archive(payload)
    return {"ticker": ticker, "ins_code": str(entry["insCode"]), "instrument_name": entry["lVal30"]}


def parse_history(payload: bytes, ticker: str, code: str) -> list[dict[str, str]]:
    observations = json.loads(payload).get("closingPriceDaily")
    if not isinstance(observations, list) or not observations:
        raise ValueError(f"Empty history for {ticker}")
    rows = {}
    for source in observations:
        day = datetime.strptime(str(source["dEven"]), "%Y%m%d").date().isoformat()
        close, trades, volume = source["pClosing"], source["zTotTran"], source["qTotTran5J"]
        if not isinstance(close, (int, float)) or close <= 0 or trades < 0 or volume < 0:
            raise ValueError(f"Invalid history for {ticker} on {day}")
        row = {"source_date_gregorian": day, "ins_code": code, "ticker": ticker,
               "closing_price_irr": str(close), "trade_count": str(trades),
               "trade_volume": str(volume), "has_trade": str(trades > 0 and volume > 0).lower()}
        if day in rows and rows[day] != row:
            raise ValueError(f"Conflicting duplicate for {ticker} on {day}")
        rows[day] = row
    return [rows[d] for d in sorted(rows)]


def collect() -> list[dict[str, str]]:
    instruments = []
    for ticker in TICKERS:
        instrument = discover(ticker)
        code = instrument["ins_code"]
        payload = fetch(HISTORY.format(code))
        rows = parse_history(payload, ticker, code)
        path = RAW / f"{code}.csv"
        if path.exists():
            with path.open(encoding="utf-8", newline="") as file:
                existing = {row["source_date_gregorian"]: row for row in csv.DictReader(file)}
            for row in rows:
                old = existing.get(row["source_date_gregorian"])
                if old is not None and old != row:
                    raise ValueError(f"Historical revision for {ticker} on {row['source_date_gregorian']}")
                existing[row["source_date_gregorian"]] = row
            rows = [existing[d] for d in sorted(existing)]
        archive(payload)
        atomic_csv(path, FIELDS, rows)
        instrument["first_date"] = rows[0]["source_date_gregorian"]
        instrument["last_date"] = rows[-1]["source_date_gregorian"]
        instrument["daily_rows"] = str(len(rows))
        instruments.append(instrument)
    atomic_csv(MANIFEST, ("ticker", "ins_code", "instrument_name", "first_date", "last_date", "daily_rows"), instruments)
    return instruments


if __name__ == "__main__":
    print(json.dumps(collect(), ensure_ascii=True, indent=2))
