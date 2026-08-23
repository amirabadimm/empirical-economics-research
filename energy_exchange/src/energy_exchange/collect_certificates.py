"""Archive and summarize Iran Energy Exchange certificate histories from TSETMC."""

from __future__ import annotations

import argparse
import csv
import json
import os
import time
import urllib.parse
from datetime import datetime, timezone
from pathlib import Path

import requests


BASE = "https://cdn.tsetmc.com/api"
SEARCH_TERMS = (
    "صرفه",
    "ظرفیت",
    "تجدیدپذیر",
    "گواهی سپرده",
    "نفت خام",
    "میعانات گازی",
    "نفتا",
    "برش هیدروکربنی",
    "اتانول",
)


def get_json(session: requests.Session, url: str, retries: int = 4) -> dict:
    for attempt in range(retries):
        try:
            response = session.get(url, timeout=60)
            response.raise_for_status()
            return response.json()
        except (requests.RequestException, ValueError):
            if attempt + 1 == retries:
                raise
            time.sleep(2**attempt)
    raise AssertionError("unreachable")


def family(row: dict) -> str:
    text = f"{row.get('lVal18AFC', '')} {row.get('lVal30', '')}"
    if "صرفه" in text:
        return "energy_saving"
    if "ظرفيت" in text or "ظرفیت" in text:
        return "capacity"
    if "تجديدپذير" in text or "تجدیدپذیر" in text:
        return "renewable_production"
    return "commodity_deposit"


def is_certificate(row: dict) -> bool:
    name = row.get("lVal30", "")
    return row.get("flow") == 6 and ("گواهي" in name or "گواهی" in name)


def atomic_json(path: Path, payload: object) -> None:
    temp = path.with_suffix(path.suffix + ".tmp")
    temp.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    os.replace(temp, path)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-dir", type=Path, default=Path(__file__).parents[2])
    args = parser.parse_args()
    project = args.project_dir.resolve()
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    raw = project / "data" / "raw" / "certificates" / stamp
    raw.mkdir(parents=True, exist_ok=False)
    session = requests.Session()
    session.headers["User-Agent"] = "energy-exchange-research/0.1"

    searches: dict[str, dict] = {}
    registry: dict[str, dict] = {}
    for term in SEARCH_TERMS:
        url = f"{BASE}/Instrument/GetInstrumentSearch/{urllib.parse.quote(term)}"
        payload = get_json(session, url)
        searches[term] = payload
        for row in payload.get("instrumentSearch", []):
            if is_certificate(row):
                item = dict(row)
                item["family"] = family(row)
                registry[str(row["insCode"])] = item
        time.sleep(0.15)
    atomic_json(raw / "instrument_searches.json", searches)
    atomic_json(raw / "instrument_registry.json", list(registry.values()))

    histories: dict[str, list[dict]] = {}
    for code in sorted(registry):
        url = f"{BASE}/ClosingPrice/GetClosingPriceDailyList/{code}/0"
        payload = get_json(session, url)
        histories[code] = payload.get("closingPriceDaily", [])
        atomic_json(raw / f"history_{code}.json", payload)
        time.sleep(0.15)

    interim = project / "data" / "interim"
    processed = project / "data" / "processed"
    interim.mkdir(parents=True, exist_ok=True)
    processed.mkdir(parents=True, exist_ok=True)
    daily_path = interim / "certificate_daily.csv"
    daily_fields = [
        "insCode", "symbol", "name", "family", "date", "trade_count", "volume",
        "value_rial", "close", "last_price", "price_min", "price_max", "has_trade",
    ]
    all_rows: list[dict] = []
    for code, rows in histories.items():
        meta = registry[code]
        for row in rows:
            all_rows.append({
                "insCode": code,
                "symbol": meta.get("lVal18AFC", ""),
                "name": meta.get("lVal30", ""),
                "family": meta["family"],
                "date": row.get("dEven"),
                "trade_count": row.get("zTotTran", 0),
                "volume": row.get("qTotTran5J", 0),
                "value_rial": row.get("qTotCap", 0),
                "close": row.get("pClosing", 0),
                "last_price": row.get("pDrCotVal", 0),
                "price_min": row.get("priceMin", 0),
                "price_max": row.get("priceMax", 0),
                "has_trade": int((row.get("zTotTran") or 0) > 0 and (row.get("qTotTran5J") or 0) > 0),
            })
    all_rows.sort(key=lambda x: (x["insCode"], x["date"] or 0))
    temp_daily = daily_path.with_suffix(".csv.tmp")
    with temp_daily.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=daily_fields)
        writer.writeheader()
        writer.writerows(all_rows)
    os.replace(temp_daily, daily_path)

    summary_fields = [
        "insCode", "symbol", "name", "family", "first_record", "last_record",
        "record_days", "traded_days", "traded_day_pct", "total_trades", "total_volume",
        "total_value_rial", "first_trade", "last_trade", "traded_days_last_90_records",
    ]
    summaries = []
    for code, meta in sorted(registry.items()):
        rows = [x for x in all_rows if x["insCode"] == code]
        traded = [x for x in rows if x["has_trade"]]
        recent = sorted(rows, key=lambda x: x["date"], reverse=True)[:90]
        summaries.append({
            "insCode": code,
            "symbol": meta.get("lVal18AFC", ""),
            "name": meta.get("lVal30", ""),
            "family": meta["family"],
            "first_record": min((x["date"] for x in rows), default=""),
            "last_record": max((x["date"] for x in rows), default=""),
            "record_days": len(rows),
            "traded_days": len(traded),
            "traded_day_pct": round(100 * len(traded) / len(rows), 2) if rows else 0,
            "total_trades": sum(float(x["trade_count"] or 0) for x in traded),
            "total_volume": sum(float(x["volume"] or 0) for x in traded),
            "total_value_rial": sum(float(x["value_rial"] or 0) for x in traded),
            "first_trade": min((x["date"] for x in traded), default=""),
            "last_trade": max((x["date"] for x in traded), default=""),
            "traded_days_last_90_records": sum(int(x["has_trade"]) for x in recent),
        })
    summary_path = processed / "certificate_activity_by_symbol.csv"
    temp_summary = summary_path.with_suffix(".csv.tmp")
    with temp_summary.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=summary_fields)
        writer.writeheader()
        writer.writerows(summaries)
    os.replace(temp_summary, summary_path)
    print(json.dumps({"snapshot": str(raw), "symbols": len(registry), "daily_rows": len(all_rows)}, ensure_ascii=True))


if __name__ == "__main__":
    main()
