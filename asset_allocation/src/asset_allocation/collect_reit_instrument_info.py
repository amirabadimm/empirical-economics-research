"""Archive TSETMC instrument-info responses and publish a date-explicit REIT unit table.

Run with PYTHONPATH=src: python -m asset_allocation.collect_reit_instrument_info
The snapshots are immutable; a same-day response change raises rather than overwrites evidence.
"""
from __future__ import annotations

import hashlib
import json
import os
import tempfile
from datetime import date
from pathlib import Path

import jdatetime
import pandas as pd
import requests

from asset_allocation.build_reit_assembly_reinvestment import FUNDS, ROOT

SNAPSHOTS = ROOT / "data/raw/real_estate_funds/instrument_info_snapshots"
OUTPUT = ROOT / "data/processed/analysis/reit_tsetmc_instrument_info.csv"
PROFILES = ROOT / "data/processed/analysis/reit_fund_profiles.csv"
FIPIRAN_SNAPSHOTS = ROOT / "data/raw/real_estate_funds/fipiran_snapshots"
FIPIRAN_URL = "https://www.fipiran.com/services/fund/fundcompare/"
BASE = "https://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/"


def atomic_bytes(path: Path, content: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as temp:
        temp.write(content)
        temp_name = temp.name
    try:
        os.replace(temp_name, path)
    finally:
        Path(temp_name).unlink(missing_ok=True)


def collect() -> pd.DataFrame:
    profiles = pd.read_csv(PROFILES, dtype={"ins_code": str})
    if set(profiles.ins_code) != set(FUNDS):
        raise ValueError("Profile roster does not match the eight configured REITs")
    profile_by_code = profiles.set_index("ins_code")
    session = requests.Session()
    fipiran_response = None
    for attempt in range(3):
        try:
            fipiran_response = session.post(
                FIPIRAN_URL, json={"regNos": [], "showMarketMakers": False},
                headers={"Referer": "https://www.fipiran.com/", "User-Agent": "Mozilla/5.0"},
                timeout=20,
            )
            fipiran_response.raise_for_status()
            break
        except requests.RequestException:
            if attempt == 2:
                raise
    assert fipiran_response is not None
    fipiran_payload = fipiran_response.json()
    fipiran_funds = {str(x["insCode"]): x for x in fipiran_payload["items"]
                     if x.get("fundType") == 18 and x.get("insCode")}
    if set(fipiran_funds) != set(FUNDS):
        raise ValueError("FIPIRAN real estate fund roster differs from the eight configured REITs")
    fipiran_bytes = (json.dumps(fipiran_payload, ensure_ascii=False, sort_keys=True,
                                separators=(",", ":")) + "\n").encode("utf-8")
    digest = hashlib.sha256(fipiran_bytes).hexdigest()
    fipiran_snapshot = FIPIRAN_SNAPSHOTS / f"fundcompare_{date.today():%Y%m%d}_{digest}.json"
    if not fipiran_snapshot.exists():
        atomic_bytes(fipiran_snapshot, fipiran_bytes)
    rows = []
    for code, fund in FUNDS.items():
        url = BASE + code
        response = session.get(url, timeout=20)
        response.raise_for_status()
        payload = response.json()
        info = payload["instrumentInfo"]
        if str(info["insCode"]) != code:
            raise ValueError(f"Instrument mismatch: {code}")
        source_day = str(info["dEven"])
        unit_count = int(info["zTitad"])
        if len(source_day) != 8 or unit_count <= 0:
            raise ValueError(f"Invalid source date or units: {code}")
        canonical = (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")
        snapshot = SNAPSHOTS / f"{code}_{source_day}_{hashlib.sha256(canonical).hexdigest()}.json"
        if snapshot.exists():
            if snapshot.read_bytes() != canonical:
                raise ValueError(f"Snapshot hash collision or corruption: {snapshot}")
        else:
            atomic_bytes(snapshot, canonical)
        fi = fipiran_funds[code]
        if int(fi["investedUnits"]) != unit_count:
            raise ValueError(f"FIPIRAN/TSETMC unit-count mismatch: {code}")
        nav_day = date.fromisoformat(fi["date"][:10])
        nav_j = jdatetime.date.fromgregorian(date=nav_day)
        nav_irr = int(fi["netAsset"])
        if nav_irr <= 0 or abs(int(fi["cancelNav"]) * unit_count - nav_irr) / nav_irr > 0.001:
            raise ValueError(f"FIPIRAN NAV fails per-unit/unit-count cross-check: {code}")
        profile = profile_by_code.loc[code]
        close_day = str(profile.latest_close_date_gregorian)
        close_irr = float(profile.latest_close_irr)
        if date.fromisoformat(close_day) > date(int(source_day[:4]), int(source_day[4:6]), int(source_day[6:])):
            raise ValueError(f"Unit observation predates close: {code}")
        rows.append({
            "fund": fund,
            "fund_persian": profile.fund_persian,
            "ins_code": code,
            "tsetmc_instrument_date_gregorian": f"{source_day[:4]}-{source_day[4:6]}-{source_day[6:]}",
            "tsetmc_units_zTitad": unit_count,
            "tsetmc_etf_issued_unit_date_gregorian": (f"{str(info['etfUnitDeven'])[:4]}-{str(info['etfUnitDeven'])[4:6]}-{str(info['etfUnitDeven'])[6:]}" if int(info.get("etfUnitDeven") or 0) else None),
            "latest_close_date_gregorian": close_day,
            "latest_close_irr": close_irr,
            "indicative_cap_with_latest_close_billion_toman": close_irr * unit_count / 1e10,
            "same_date_market_cap_verified": source_day == close_day.replace("-", ""),
            "official_nav_billion_toman": nav_irr / 1e10,
            "official_nav_date_gregorian": nav_day.isoformat(),
            "official_nav_date_jalali": f"{nav_j.year:04}/{nav_j.month:02}/{nav_j.day:02}",
            "fipiran_invested_units": int(fi["investedUnits"]),
            "fipiran_cancel_nav_per_unit_irr": int(fi["cancelNav"]),
            "fipiran_manager": fi.get("manager"),
            "fipiran_source_url": FIPIRAN_URL,
            "fipiran_snapshot_path": fipiran_snapshot.relative_to(ROOT).as_posix(),
            "tsetmc_nav_field": info.get("nav"),
            "tsetmc_nav_status": "zero_not_usable" if not info.get("nav") else "requires_unit_and_date_interpretation",
            "source_url": url,
            "snapshot_path": snapshot.relative_to(ROOT).as_posix(),
        })
    result = pd.DataFrame(rows)
    with tempfile.NamedTemporaryFile(mode="w", encoding="utf-8", newline="", dir=OUTPUT.parent, delete=False) as temp:
        result.to_csv(temp, index=False)
        temp_name = temp.name
    try:
        os.replace(temp_name, OUTPUT)
    finally:
        Path(temp_name).unlink(missing_ok=True)
    return result


if __name__ == "__main__":
    result = collect()
    print(result[["fund", "tsetmc_instrument_date_gregorian", "tsetmc_units_zTitad", "indicative_cap_with_latest_close_billion_toman"]].to_string(index=False))
