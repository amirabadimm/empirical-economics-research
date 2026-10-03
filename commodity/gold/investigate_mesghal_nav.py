"""Archive and audit Mesghal NAV endpoints without publishing canonical NAV.

Run from the workspace root. Successful and failed HTTP bodies are immutable;
each request has separate provenance. Only an unambiguous directory identity
permits a Fipiran history request. This investigation never estimates NAV.
"""
import argparse
import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import numpy as np
import pandas as pd
import requests

PROJECT = Path(__file__).resolve().parent
ARCHIVE = PROJECT / "data/raw/funds/mesghal/snapshots/nav_investigation"
REPORTS = PROJECT / "data/processed/analysis"
EXPECTED = {
    "regNo": "11899",
    "groupId": 2,
    "name": "صندوق س.کالای آگاه (مثقال)",
    "smallSymbolName": "مثقال",
    "insCode": "32469128621155736",
}


def request_archive(session, label, url, *, method="GET", params=None,
                    body=None, identity=None):
    """Archive exact response bytes before JSON parsing, including HTTP errors."""
    stamp = datetime.now(timezone.utc)
    record = {"label": label, "url": url, "method": method,
              "params": params if params is not None else parse_qs(urlsplit(url).query), "request_json": body,
              "requested_at_utc": stamp.isoformat(),
              "verified_identity": identity, "tls_verified": True}
    payload = None
    ARCHIVE.mkdir(parents=True, exist_ok=True)
    try:
        response = session.request(method, url, params=params, json=body,
                                   timeout=(15, 35))
        content = response.content
        digest = hashlib.sha256(content).hexdigest()
        path = ARCHIVE / f"{digest}.body"
        if not path.exists():
            with path.open("xb") as handle:
                handle.write(content)
        elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
            raise ValueError(f"Corrupt existing snapshot: {path}")
        record.update(url=response.url, status_code=response.status_code,
                      retrieved_at_utc=datetime.now(timezone.utc).isoformat(),
                      sha256=digest, bytes=len(content),
                      snapshot=str(path.relative_to(PROJECT)),
                      content_type=response.headers.get("Content-Type"))
        # Parsing happens only after archival.
        try:
            payload = response.json()
        except ValueError:
            record["non_json_prefix"] = response.text[:300]
        if response.status_code != 200:
            record["http_error"] = response.text[:500]
    except requests.RequestException as exc:
        record["transport_error"] = f"{type(exc).__name__}: {exc}"
    metadata = ARCHIVE / f"{stamp.strftime('%Y%m%dT%H%M%S%fZ')}_{label}.metadata.json"
    with metadata.open("x", encoding="utf-8") as handle:
        json.dump(record, handle, ensure_ascii=False, indent=2)
    print(json.dumps(record, ensure_ascii=True), flush=True)
    return payload, record


def audit_history(rows, date_field="date", nav_field="cancelNav"):
    if not isinstance(rows, list):
        return {"accepted": False, "reason": "History is not an array"}
    if not rows:
        return {"accepted": False, "reason": "Empty history array", "rows": 0,
                "distinct_dates": 0, "valid_daily_observations": 0,
                "earliest_date": None, "latest_date": None,
                "invalid_nav_rows": 0, "duplicate_rows": 0,
                "conflicting_dates": 0, "nav_field_observed": False}
    frame = pd.DataFrame(rows)
    if date_field not in frame or nav_field not in frame:
        return {"accepted": False, "reason": "Required history fields absent",
                "rows": len(frame), "columns": frame.columns.tolist()}
    dates = pd.to_datetime(frame[date_field].astype(str).str[:10], errors="coerce")
    nav = pd.to_numeric(frame[nav_field], errors="coerce")
    good = dates.notna() & np.isfinite(nav) & nav.gt(0)
    comparison = pd.DataFrame({"date": dates, "nav": nav})
    conflicts = comparison.groupby("date").nav.nunique(dropna=False).gt(1)
    return {"accepted": bool(good.all() and not conflicts.any()),
            "rows": len(frame), "distinct_dates": int(dates.nunique()),
            "valid_daily_observations": int(dates[good].nunique()),
            "earliest_date": str(dates.min().date()) if dates.notna().any() else None,
            "latest_date": str(dates.max().date()) if dates.notna().any() else None,
            "null_nav_rows": int(nav.isna().sum()), "zero_nav_rows": int(nav.eq(0).sum()),
            "invalid_nav_rows": int((~np.isfinite(nav) | nav.le(0)).sum()),
            "invalid_date_rows": int(dates.isna().sum()),
            "duplicate_rows": int(dates.duplicated().sum()),
            "conflicting_dates": int(conflicts.sum()),
            "nav_field_observed": True, "sample_raw_rows": [rows[0], rows[-1]]}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--probe-url", help="Archive an additional public source URL only")
    parser.add_argument("--label", default="additional_probe")
    args = parser.parse_args()
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://www.fipiran.com/"})
    if args.probe_url:
        request_archive(session, args.label, args.probe_url)
        return
    report = {"checked_at_utc": datetime.now(timezone.utc).isoformat(), "requests": []}
    directory, record = request_archive(
        session, "fipiran_directory", "https://www.fipiran.com/services/fund/fundcompare/",
        method="POST", body={"regNos": [], "showMarketMakers": False})
    report["requests"].append(record)
    entries = directory.get("items", []) if isinstance(directory, dict) else []
    candidates = [row for row in entries if str(row.get("regNo")) == EXPECTED["regNo"]]
    report["registration_candidates"] = candidates
    group_candidates = [row for row in candidates if row.get("groupId") == EXPECTED["groupId"]]
    matches = [row for row in group_candidates if all(
        str(row.get(key)) == str(value) for key, value in EXPECTED.items())]
    report["identity_verified"] = record.get("status_code") == 200 and len(matches) == 1 and len(group_candidates) == 1
    if report["identity_verified"]:
        report["verified_identity"] = EXPECTED
        rows, record = request_archive(
            session, "fipiran_history", "https://www.fipiran.com/services/chart/getfundchart",
            params={"regno": int(EXPECTED["regNo"]), "groupId": EXPECTED["groupId"],
                    "showAll": "true"}, identity=EXPECTED)
        report["requests"].append(record)
        report["fipiran_history_audit"] = audit_history(rows)
        if record.get("status_code") != 200:
            report["fipiran_history_audit"]["accepted"] = False
            report["fipiran_history_audit"]["reason"] = "Historical endpoint request failed"
    else:
        report["fipiran_history_audit"] = {"accepted": False, "reason": "Identity not verified; chart request stopped"}
    instrument, record = request_archive(
        session, "tsetmc_instrument", f"https://cdn.tsetmc.com/api/Instrument/GetInstrumentInfo/{EXPECTED['insCode']}")
    report["requests"].append(record)
    report["tsetmc_instrument"] = instrument
    latest, record = request_archive(
        session, "tsetmc_latest", f"https://cdn.tsetmc.com/api/Fund/GetETFByInsCode/{EXPECTED['insCode']}")
    report["requests"].append(record)
    report["tsetmc_latest"] = latest
    detail, record = request_archive(
        session, "tsetmc_detail", f"https://cdn.tsetmc.com/api/Fund/GetFundInDetail/{EXPECTED['regNo']}")
    report["requests"].append(record)
    if isinstance(detail, dict) and isinstance(detail.get("fund"), dict):
        report["tsetmc_detail_identity"] = {k: v for k, v in detail["fund"].items() if k != "stats"}
        report["tsetmc_detail_audit"] = audit_history(detail["fund"].get("stats"), "recordDate", "navRed")
        report["tsetmc_detail_accepted"] = False  # Explicit identity review required.
    if matches:
        for index, domain in enumerate(matches[0].get("websiteAddress", [])):
            _, record = request_archive(session, f"manager_{index}", "https://" + domain.removeprefix("https://").removeprefix("http://"))
            report["requests"].append(record)
    report["conclusion"] = (
        "YES - verified Fipiran historical redemption NAV retrieved; integration still requires review"
        if report["fipiran_history_audit"].get("accepted")
        else "NO - a verifiable historical redemption NAV series for Mesghal could not be obtained from these requests"
    )
    REPORTS.mkdir(parents=True, exist_ok=True)
    target = REPORTS / f"mesghal_nav_investigation_{datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%S%fZ')}.json"
    with target.open("x", encoding="utf-8") as handle:
        json.dump(report, handle, ensure_ascii=False, indent=2)
    print("REPORT", target, flush=True)
    print("FIPIRAN_AUDIT", json.dumps(report["fipiran_history_audit"], ensure_ascii=True), flush=True)


if __name__ == "__main__":
    main()
