from __future__ import annotations

import json
import re
from pathlib import Path
from urllib.parse import quote

from .common import (ROOT, UNDERLYING_CODE, UNDERLYING_SYMBOL, archive_json,
                     atomic_csv, atomic_bytes, fetch_json, jalali_to_gregorian, session, today)

BASE = "https://cdn.tsetmc.com/api/Instrument/"
SEARCH_LIMIT = 40
FAMILIES = ("ضهرم", "طهرم")
NAME_RE = re.compile(r"^اختیار([خف])\s+اهرم-(\d+)-(\d{4}/\d{2}/\d{2})$")
MASTER_COLUMNS = ["ins_code", "symbol", "underlying_ins_code", "underlying_symbol",
                  "option_type", "strike", "expiration_date", "expiration_jalali",
                  "first_available_date", "last_available_date",
                  "optionbaaz_first_date", "optionbaaz_last_date", "status", "tsetmc_name",
                  "tsetmc_instrument_id", "tsetmc_isin", "discovery_sources"]


def discover(root: Path = ROOT, *, delay: float = 0.25) -> list[dict]:
    client = session()
    candidates: dict[str, dict] = {}
    sources: dict[str, set[str]] = {}
    query_records = []

    def search(prefix: str) -> None:
        body = fetch_json(client, BASE + "GetInstrumentSearch/" + quote(prefix), delay=delay)
        archive = archive_json(root / "data/raw/tsetmc/search", body)
        entries = body.get("instrumentSearch")
        if not isinstance(entries, list):
            raise ValueError(f"Unexpected search response for {prefix!r}")
        query_records.append({"query": prefix, "count": len(entries), "archive": str(archive.relative_to(root))})
        for entry in entries:
            symbol = str(entry.get("lVal18AFC") or "")
            code = str(entry.get("insCode") or "")
            if symbol.startswith(FAMILIES) and code.isdecimal():
                candidates[code] = entry
                sources.setdefault(code, set()).add("search")
        if len(entries) >= SEARCH_LIMIT:
            if len(prefix) >= 10:
                raise ValueError(f"Search still capped at deepest prefix: {prefix!r}")
            for digit in "0123456789":
                search(prefix + digit)

    for family in FAMILIES:
        search(family)
    watch = fetch_json(client, BASE + "GetInstrumentOptionMarketWatch/1", delay=delay)
    watch_archive = archive_json(root / "data/raw/tsetmc/market_watch", watch)
    watch_entries = watch.get("instrumentOptMarketWatch")
    if not isinstance(watch_entries, list):
        raise ValueError("Unexpected option market watch response")
    for item in watch_entries:
        if str(item.get("uaInsCode")) != UNDERLYING_CODE:
            continue
        for suffix in ("C", "P"):
            code = str(item.get(f"insCode_{suffix}") or "")
            if not code.isdecimal():
                continue
            candidates.setdefault(code, {"insCode": code,
                                         "lVal18AFC": item.get(f"lVal18AFC_{suffix}"),
                                         "lVal30": item.get(f"lVal30_{suffix}")})
            sources.setdefault(code, set()).add("market_watch")

    rows = []
    errors = []
    for code, candidate in sorted(candidates.items()):
        try:
            identity_body = fetch_json(client, BASE + "GetInstrumentIdentity/" + code, delay=delay)
            archive_json(root / "data/raw/tsetmc/identity" / code, identity_body)
            identity = identity_body.get("instrumentIdentity") or {}
            symbol = str(identity.get("lVal18AFC") or candidate.get("lVal18AFC") or "")
            name = str(identity.get("lVal30") or candidate.get("lVal30") or "")
            normalized_name = name.replace("ي", "ی").replace("ك", "ک")
            match = NAME_RE.fullmatch(normalized_name)
            if (not symbol.startswith(FAMILIES) or not match
                    or str(identity.get("cSocCSAC") or "").upper() != "AHRM"):
                errors.append({"ins_code": code, "reason": "underlying_or_metadata_unverified",
                               "symbol": symbol, "name": name})
                continue
            option_type = "call" if match.group(1) == "خ" else "put"
            if (option_type == "call") != symbol.startswith("ضهرم"):
                errors.append({"ins_code": code, "reason": "type_symbol_conflict", "symbol": symbol})
                continue
            expiry = jalali_to_gregorian(match.group(3))
            rows.append({"ins_code": code, "symbol": symbol,
                         "underlying_ins_code": UNDERLYING_CODE,
                         "underlying_symbol": UNDERLYING_SYMBOL,
                         "option_type": option_type, "strike": int(match.group(2)),
                         "expiration_date": expiry, "expiration_jalali": match.group(3),
                         "first_available_date": "", "last_available_date": "",
                         "optionbaaz_first_date": "", "optionbaaz_last_date": "",
                         "status": "expired" if expiry < today() else "active",
                         "tsetmc_name": name, "tsetmc_instrument_id": identity.get("instrumentID") or "",
                         "tsetmc_isin": identity.get("cIsin") or "",
                         "discovery_sources": ";".join(sorted(sources[code]))})
        except Exception as exc:
            errors.append({"ins_code": code, "reason": type(exc).__name__, "detail": str(exc)[:200]})
    rows.sort(key=lambda row: (row["expiration_date"], row["option_type"], row["strike"], row["ins_code"]))
    processed = root / "data/processed"
    atomic_csv(processed / "ahrom_option_contracts.csv", rows, MASTER_COLUMNS)
    audit = {"date": today(), "search_queries": query_records,
             "market_watch_archive": str(watch_archive.relative_to(root)),
             "candidate_count": len(candidates), "verified_count": len(rows), "errors": errors}
    atomic_bytes(processed / "discovery_audit.json", json.dumps(audit, ensure_ascii=False, indent=2).encode())
    return rows
