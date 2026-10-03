"""Audit NAV identity, archived provenance, coverage, and live provider agreement.

This audit writes response snapshots and derived reports only. It never updates
canonical raw CSVs. Use --live for a fresh audit; otherwise replay the latest
archived reliability requests. Comparison dates are explicit and inclusive.
"""
import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import numpy as np
import pandas as pd
import requests

PROJECT = Path(__file__).resolve().parent
ROOT = PROJECT.parents[1]
sys.path.insert(0, str(ROOT))
from shared.market_analysis.bubble_distribution import _atomic_csv

FUNDS = ("ayar", "tala", "kahroba", "ganj", "gohar")
OUT = PROJECT / "data/processed/analysis/nav_reliability"


def request(session, fund, label, url, live, params=None, body=None, as_json=True):
    folder = PROJECT / f"data/raw/funds/{fund}/snapshots/reliability"
    if not live:
        records = sorted(folder.glob(f"*_{label}.metadata.json"))
        if not records:
            raise FileNotFoundError(f"No archived {fund}/{label} request")
        meta = json.loads(records[-1].read_text(encoding="utf-8"))
        content = (folder / f"{meta['sha256']}.json").read_bytes()
        assert hashlib.sha256(content).hexdigest() == meta["sha256"]
        return (json.loads(content) if as_json else content.decode("utf-8", errors="replace")), meta
    stamp = datetime.now(timezone.utc)
    response = session.request("POST" if body is not None else "GET", url,
                               params=params, json=body, timeout=(15, 45))
    content = response.content
    digest = hashlib.sha256(content).hexdigest()
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / f"{digest}.json"
    if not path.exists():
        with path.open("xb") as handle:
            handle.write(content)
    else:
        assert hashlib.sha256(path.read_bytes()).hexdigest() == digest
    meta = {"url": response.url, "params": params, "request_json": body,
            "method": response.request.method, "status": response.status_code,
            "retrieved_at_utc": datetime.now(timezone.utc).isoformat(),
            "sha256": digest, "snapshot": str(path.relative_to(PROJECT)),
            "tls_verified": True}
    with (folder / f"{stamp.strftime('%Y%m%dT%H%M%S%fZ')}_{label}.metadata.json").open("x", encoding="utf-8") as handle:
        json.dump(meta, handle, ensure_ascii=False, indent=2)
    response.raise_for_status()
    return (response.json() if as_json else response.text), meta


def normalize(rows, provider):
    if not isinstance(rows, list) or not rows:
        raise ValueError(f"Empty {provider} history")
    date_col, nav_col = ("date", "cancelNav") if provider == "fipiran" else ("recordDate", "navRed")
    data = pd.DataFrame(rows)
    result = pd.DataFrame({"date": pd.to_datetime(data[date_col].astype(str).str[:10], errors="raise").dt.strftime("%Y-%m-%d"),
                           "nav": pd.to_numeric(data[nav_col], errors="raise")})
    if result.date.isna().any() or not (np.isfinite(result.nav) & result.nav.gt(0)).all():
        raise ValueError(f"Invalid {provider} dates/NAV")
    if result.groupby("date").nav.nunique(dropna=False).gt(1).any():
        raise ValueError(f"Conflicting {provider} date values")
    stats = {"response_rows": len(result), "duplicate_rows": int(result.date.duplicated().sum()),
             "invalid_rows": 0, "conflicting_dates": 0}
    result = result.drop_duplicates("date").sort_values("date")
    stats.update(unique_dates=len(result), earliest=result.date.min(), latest=result.date.max())
    return result, stats


def saved_provenance(fund, filename):
    raw = PROJECT / f"data/raw/funds/{fund}"
    path = raw / filename
    if not path.exists():
        return None, {"exists": False}
    frame = pd.read_csv(path)
    bad = []
    hashes = {}
    identity_errors = []
    cfg = json.loads((PROJECT / "config/funds.json").read_text(encoding="utf-8"))[fund]
    for digest, group in frame.groupby("source_snapshot"):
        candidates = list((raw / "snapshots").glob(f"**/{digest}.json"))
        # A later audit may archive identical bytes in another folder with
        # per-request metadata. Prefer the collector's original paired metadata.
        candidates.sort(key=lambda p: (not p.with_name(f"{digest}.metadata.json").exists(), str(p)))
        if not candidates:
            bad.extend(group.date.tolist())
            continue
        content = candidates[0].read_bytes()
        if hashlib.sha256(content).hexdigest() != digest:
            bad.extend(group.date.tolist())
            continue
        payload = json.loads(content)
        metadata_path = candidates[0].with_name(f"{digest}.metadata.json")
        if not metadata_path.exists():
            identity_errors.append(digest)
        else:
            metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
            url = urlsplit(metadata["url"])
            query = parse_qs(url.query)
            if filename == "price.csv":
                identity_ok = url.path.endswith(f"/GetClosingPriceDailyList/{cfg['ins_code']}/0")
            elif filename == "nav_fipiran.csv":
                identity_ok = query.get("regno") == [str(cfg["nav_reg_no"])] and query.get("groupId") == [str(cfg.get("fipiran_group_id", 0))]
            else:
                identity_ok = url.path.endswith(f"/GetFundInDetail/{cfg['nav_reg_no']}") and payload["fund"].get("mfName") == cfg["nav_fund_name"]
            if not identity_ok:
                identity_errors.append(digest)
        if filename == "price.csv":
            rows = payload["closingPriceDaily"]
            source = {str(r["dEven"]): (r["pClosing"], r["qTotTran5J"], r["zTotTran"]) for r in rows}
            for row in group.itertuples():
                if source.get(row.date.replace("-", "")) != (row.closing_price_irr, row.trade_volume, row.trade_count):
                    bad.append(row.date)
        else:
            if isinstance(payload, list):
                key = "cancelNav" if filename == "nav_fipiran.csv" else "redemptionNav"
                source = {(r["date"][:10], float(r[key])) for r in payload}
            else:
                source = {(r["recordDate"][:10], float(r["navRed"])) for r in payload["fund"]["stats"]}
            for row in group.itertuples():
                if (row.date, float(row.redemption_nav_irr)) not in source:
                    bad.append(row.date)
        hashes[digest] = str(candidates[0].relative_to(PROJECT))
    col = "closing_price_irr" if filename == "price.csv" else "redemption_nav_irr"
    numbers = pd.to_numeric(frame[col], errors="coerce")
    return frame, {"exists": True, "rows": len(frame), "earliest": frame.date.min(), "latest": frame.date.max(),
                   "duplicate_dates": int(frame.date.duplicated().sum()),
                   "invalid_values": int((~np.isfinite(numbers) | numbers.le(0)).sum()),
                   "source_hash_missing_rows": int(frame.source_snapshot.isna().sum()),
                   "snapshot_identity_errors": identity_errors,
                   "untraceable_rows": len(bad), "untraceable_dates": bad, "snapshots": hashes}


def compare(a, b, fund, kind, prices, start, end):
    merged = a[["date", "nav"]].merge(b[["date", "nav"]], on="date", suffixes=("_a", "_b"), validate="one_to_one")
    merged = merged.loc[merged.date.between(start, end)].copy()
    merged["fund"] = fund
    merged["comparison"] = kind
    merged["relative_difference_pct"] = 100 * (merged.nav_b / merged.nav_a - 1)
    merged = merged.merge(prices[["date", "closing_price_irr"]], on="date", how="left", validate="one_to_one")
    merged["traded"] = merged.closing_price_irr.notna()
    merged["bubble_difference_pp"] = 100 * merged.closing_price_irr * (1 / merged.nav_b - 1 / merged.nav_a)
    different = merged.loc[merged.nav_a.ne(merged.nav_b)].copy()
    metric = {"overlap": len(merged), "different": len(different),
              "max_abs_difference_pct": float(different.relative_difference_pct.abs().max()) if len(different) else 0,
              "traded_overlap": int(merged.traded.sum()), "traded_different": int(different.traded.sum()),
              "max_traded_bubble_difference_pp": float(different.bubble_difference_pp.abs().max()) if different.traded.any() else 0}
    a_dates = set(a.loc[a.date.between(start, end), "date"])
    b_dates = set(b.loc[b.date.between(start, end), "date"])
    metric.update(a_only_dates=sorted(a_dates - b_dates), b_only_dates=sorted(b_dates - a_dates))
    return metric, different


def persian(value):
    return str(value).replace("ي", "ی").replace("ك", "ک").strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    parser.add_argument("--start", default="2024-09-28")
    parser.add_argument("--end", default="2026-09-28")
    args = parser.parse_args()
    configs = json.loads((PROJECT / "config/funds.json").read_text(encoding="utf-8"))
    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0", "Referer": "https://www.fipiran.com/"})
    directory, directory_meta = request(session, "ayar", "directory", "https://www.fipiran.com/services/fund/fundcompare/",
                                        args.live, body={"regNos": [], "showMarketMakers": False})
    report = {"audited_at_utc": datetime.now(timezone.utc).isoformat(), "window": [args.start, args.end],
              "fresh_requests": args.live, "directory_request": directory_meta, "funds": {}}
    disagreements = []
    coverage = []
    jumps = []
    for fund in FUNDS:
        cfg = configs[fund]
        group_id = cfg.get("fipiran_group_id", 0)
        identity = [r for r in directory["items"] if str(r.get("regNo")) == str(cfg["nav_reg_no"]) and r.get("groupId") == group_id]
        if len(identity) != 1 or identity[0].get("name") != cfg["nav_fund_name"] or str(identity[0].get("insCode")) != cfg["ins_code"]:
            raise ValueError(f"{fund}: Fipiran identity mismatch")
        identity = identity[0]
        entry = {"identity": identity, "identity_passed": True, "requests": {}, "saved": {}, "comparisons": {}}
        report["funds"][fund] = entry
        saved = {}
        for filename in ["price.csv", "nav_fipiran.csv", "nav_tsetmc.csv" if fund == "ayar" else "nav.csv"]:
            frame, stats = saved_provenance(fund, filename)
            entry["saved"][filename] = stats
            if frame is not None:
                saved[filename] = frame
        prices = saved["price.csv"]
        traded = prices.loc[(prices.trade_volume > 0) & (prices.trade_count > 0)].copy()
        base = "https://cdn.tsetmc.com/api"
        instrument, meta = request(session, fund, "instrument", f"{base}/Instrument/GetInstrumentInfo/{cfg['ins_code']}", args.live)
        entry["requests"]["instrument"] = meta
        info = instrument["instrumentInfo"]
        if str(info.get("insCode")) != cfg["ins_code"] or persian(info.get("lVal18AFC")) != persian(identity["smallSymbolName"]):
            raise ValueError(f"{fund}: TSETMC instrument identity mismatch")
        entry["tsetmc_instrument_identity"] = {k: info.get(k) for k in ["insCode", "lVal18AFC", "lVal30", "instrumentID", "etfIssuedUnit", "etfUnitDeven"]}
        fip, meta = request(session, fund, "fipiran_history", "https://www.fipiran.com/services/chart/getfundchart", args.live,
                            params={"regno": cfg["nav_reg_no"], "groupId": group_id, "showAll": "true"})
        entry["requests"]["fipiran_history"] = meta
        live_fip, entry["live_fipiran"] = normalize(fip, "fipiran")
        tse, meta = request(session, fund, "tsetmc_history", f"{base}/Fund/GetFundInDetail/{cfg['nav_reg_no']}", args.live)
        entry["requests"]["tsetmc_history"] = meta
        if tse["fund"].get("mfName") != cfg["nav_fund_name"] or int(tse["fund"].get("regNo", -1)) != cfg["nav_reg_no"]:
            raise ValueError(f"{fund}: TSETMC history identity mismatch")
        live_tse, entry["live_tsetmc"] = normalize(tse["fund"]["stats"], "tsetmc")
        entry["tsetmc_summary"] = {k: tse["fund"].get(k) for k in ["mfName", "regNo", "recordDate", "navRed", "units", "netAsset"]}
        latest, meta = request(session, fund, "latest", f"{base}/Fund/GetETFByInsCode/{cfg['ins_code']}", args.live)
        entry["requests"]["latest"] = meta
        entry["latest_etf"] = latest.get("etf")
        fresh_prices, meta = request(session, fund, "prices", f"{base}/ClosingPrice/GetClosingPriceDailyList/{cfg['ins_code']}/0", args.live)
        entry["requests"]["prices"] = meta
        fresh = pd.DataFrame(fresh_prices["closingPriceDaily"])
        entry["latest_traded_prices"] = fresh.loc[(fresh.qTotTran5J > 0) & (fresh.zTotTran > 0)].sort_values("dEven").tail(5)[["dEven", "pClosing", "qTotTran5J", "zTotTran"]].to_dict("records")
        series = {"live_tsetmc": live_tse, "live_fipiran": live_fip}
        for filename, frame in saved.items():
            if filename != "price.csv":
                series["saved_" + ("fipiran" if filename == "nav_fipiran.csv" else "tsetmc")] = frame.rename(columns={"redemption_nav_irr": "nav"})
        pairs = [("live_tsetmc", "live_fipiran")]
        if fund == "ayar" and "saved_tsetmc" in series:
            pairs.append(("saved_tsetmc", "live_fipiran"))
        for provider in ["tsetmc", "fipiran"]:
            if f"saved_{provider}" in series:
                pairs.append((f"saved_{provider}", f"live_{provider}"))
        if "saved_fipiran" in series and "saved_tsetmc" in series:
            pairs.append(("saved_tsetmc", "saved_fipiran"))
        for a, b in pairs:
            kind = a + "_vs_" + b
            metric, diff = compare(series[a], series[b], fund, kind, traded, args.start, args.end)
            entry["comparisons"][kind] = metric
            disagreements.append(diff)
        for label, frame in series.items():
            window_traded = traded.loc[traded.date.between(args.start, args.end)]
            missing = window_traded.loc[~window_traded.date.isin(frame.date), "date"].tolist()
            coverage.append({"fund": fund, "series": label, "traded_dates": len(window_traded),
                             "matched": len(window_traded) - len(missing), "missing": len(missing), "missing_dates": "|".join(missing)})
            s = frame.sort_values("date").copy()
            s["previous_nav"] = s.nav.shift(1)
            s["change_pct"] = s.nav.pct_change() * 100
            s["fund"] = fund
            s["series"] = label
            jumps.append(s.loc[s.change_pct.abs().gt(30) & s.date.between(args.start, args.end), ["fund", "series", "date", "previous_nav", "nav", "change_pct"]])
        entry["latest_history_rows"] = {"fipiran": live_fip.tail(5).to_dict("records"), "tsetmc": live_tse.tail(5).to_dict("records")}
        print(f"{fund}: identities verified; " + json.dumps({k: {m: n for m, n in v.items() if not m.endswith('_dates')}
                                                            for k, v in entry["comparisons"].items()}), flush=True)
    OUT.mkdir(parents=True, exist_ok=True)
    _atomic_csv(pd.concat(disagreements, ignore_index=True), OUT / "provider_disagreements.csv")
    _atomic_csv(pd.DataFrame(coverage), OUT / "coverage.csv")
    _atomic_csv(pd.concat(jumps, ignore_index=True), OUT / "large_nav_changes.csv")
    (OUT / "audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print("REPORT", OUT / "audit.json")


if __name__ == "__main__":
    main()
