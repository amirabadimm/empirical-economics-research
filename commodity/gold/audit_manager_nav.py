"""Corroborate saved Fipiran NAV against official manager records (audit only).

Endpoint discovery and identity evidence are recorded in NAV_RELIABILITY.md.
Manager values remain separate derived validation evidence, never replacements
for canonical Fipiran NAV. Use --live to archive fresh manager observations.
"""
import argparse
from datetime import datetime, timezone
from concurrent.futures import ThreadPoolExecutor
import json
from urllib.parse import parse_qs, urlsplit

import jdatetime
import numpy as np
import pandas as pd
import requests
from bs4 import BeautifulSoup

from audit_nav_reliability import PROJECT, OUT, FUNDS, request, compare, normalize, _atomic_csv


def trading_validation(manager_rows, window):
    """Annotate selected canonical observations without changing their values."""
    provider_report = json.loads((OUT / "audit.json").read_text(encoding="utf-8"))
    tables = []
    for fund in FUNDS:
        raw = PROJECT / f"data/raw/funds/{fund}"
        prices = pd.read_csv(raw / "price.csv")
        table = prices.loc[prices.date.between(*window) & prices.trade_volume.gt(0) & prices.trade_count.gt(0),
                           ["date", "closing_price_irr", "source_snapshot"]].rename(columns={"source_snapshot": "price_source_snapshot"})
        filename = "nav_fipiran.csv"
        selected = pd.read_csv(raw / filename)[["date", "redemption_nav_irr", "source_snapshot"]]
        table = table.merge(selected.rename(columns={"redemption_nav_irr": "selected_nav_irr", "source_snapshot": "selected_source_snapshot"}),
                            on="date", how="left", validate="one_to_one")
        for provider in ["fipiran", "tsetmc"]:
            meta = provider_report["funds"][fund]["requests"][provider + "_history"]
            payload = json.loads((PROJECT / meta["snapshot"]).read_bytes())
            frame, _ = normalize(payload if provider == "fipiran" else payload["fund"]["stats"], provider)
            table = table.merge(frame.rename(columns={"nav": f"audit_{provider}_nav_irr"}), on="date", how="left", validate="one_to_one")
        managers = manager_rows.loc[manager_rows.fund.eq(fund), ["date", "nav", "manager_source_snapshot"]]
        table = table.merge(managers.rename(columns={"nav": "manager_nav_irr"}), on="date", how="left", validate="one_to_one")
        table["fund"] = fund
        table["selected_provider"] = "fipiran_historical"
        table["validation_status"] = "no_secondary_observation"
        other = table.audit_tsetmc_nav_irr
        table.loc[other.notna() & table.selected_nav_irr.eq(other), "validation_status"] = "provider_agreement_only"
        table.loc[other.notna() & table.selected_nav_irr.ne(other), "validation_status"] = "provider_conflict"
        table.loc[table.manager_nav_irr.notna() & table.selected_nav_irr.eq(table.manager_nav_irr), "validation_status"] = "manager_agrees"
        table.loc[table.manager_nav_irr.notna() & table.selected_nav_irr.ne(table.manager_nav_irr), "validation_status"] = "manager_conflict"
        table.loc[table.selected_nav_irr.isna(), "validation_status"] = "missing_selected_nav"
        table["selected_bubble_pct"] = 100 * (table.closing_price_irr / table.selected_nav_irr - 1)
        table["manager_bubble_pct"] = 100 * (table.closing_price_irr / table.manager_nav_irr - 1)
        tables.append(table)
    result = pd.concat(tables, ignore_index=True)
    _atomic_csv(result, OUT / "trading_date_validation.csv")
    return result.groupby(["fund", "validation_status"]).size().rename("dates").reset_index().to_dict("records")


def gregorian(value):
    return jdatetime.date(*map(int, value.split("/"))).togregorian().isoformat()


def validate(frame):
    frame["nav"] = pd.to_numeric(frame.nav, errors="raise")
    if not (np.isfinite(frame.nav) & frame.nav.gt(0)).all():
        raise ValueError("Invalid manager NAV")
    pd.to_datetime(frame.date, errors="raise")
    if frame.groupby("date").nav.nunique(dropna=False).gt(1).any():
        raise ValueError("Conflicting manager NAV on same valuation date")
    return frame.drop_duplicates("date").sort_values("date")


def ganj_page(html, digest):
    soup = BeautifulSoup(html, "html.parser")
    rows = []
    for table in soup.find_all("table"):
        headers = [c.get_text(" ", strip=True) for c in table.find_all("th")]
        if "قیمت ابطال" not in headers:
            continue
        nav_index = headers.index("قیمت ابطال")
        date_index = headers.index("تاریخ")
        group_index = headers.index("نام گروه")
        for tr in table.select("tbody tr"):
            cells = [c.get_text(" ", strip=True) for c in tr.find_all("td")]
            if len(cells) != len(headers):
                continue
            if cells[group_index] != "صندوق سرمایه گذاری سیمای کاردان":
                raise ValueError("Ganj manager table group mismatch")
            rows.append({"date": gregorian(cells[date_index]), "nav": int(cells[nav_index].replace(",", "")),
                         "manager_source_snapshot": digest})
    if not rows:
        raise ValueError("No Ganj NAV table rows")
    pages = [int(parse_qs(urlsplit(a["href"]).query)["page"][0]) for a in soup.find_all("a", href=True)
             if "FundNAVList?" in a["href"] and "page" in parse_qs(urlsplit(a["href"]).query)]
    return rows, max(pages, default=1)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--live", action="store_true")
    args = parser.parse_args()
    report = {"audited_at_utc": datetime.now(timezone.utc).isoformat(), "fresh_requests": args.live,
              "window": ["2024-09-28", "2026-09-28"], "funds": {}}
    all_rows, all_diff = [], []
    for fund in ["tala", "kahroba", "gohar", "ganj"]:
        session = requests.Session()
        meta_records = []
        if fund in ["tala", "kahroba"]:
            domain = "https://lotusgoldfund.capital" if fund == "tala" else "https://kahroba.charismafunds.ir"
            identity, meta = request(session, fund, "manager_funds", domain + "/api/v1/public/fundItems", args.live)
            meta_records.append(meta)
            cfg = json.loads((PROJECT / "config/funds.json").read_text(encoding="utf-8"))[fund]
            selected = [r for r in identity if r.get("fundId") == 1]
            if len(selected) != 1 or not selected[0].get("tsetmcUrl", "").endswith("/" + cfg["ins_code"]):
                raise ValueError(f"{fund}: manager identity mismatch")
            payload, meta = request(session, fund, "manager_nav", domain + "/api/v1/public/nav/1", args.live)
            meta_records.append(meta)
            rows = [{"date": gregorian(r["jalaliDate"]), "nav": r["sellNAVPerShare"],
                     "manager_source_snapshot": meta["sha256"]} for r in payload]
        elif fund == "gohar":
            identity, meta = request(session, fund, "manager_portfolios", "https://kianfunds3.ir/api/v2/public/fund/portfolios", args.live)
            meta_records.append(meta)
            selected = [r for r in identity["data"] if r.get("id") == "1"]
            if len(selected) != 1 or selected[0].get("name") != "سرمایه گذاری در اوراق بهادار مبتنی بر طلای کیان":
                raise ValueError("Gohar manager portfolio mismatch")
            payload, meta = request(session, fund, "manager_nav", "https://kianfunds3.ir/api/v2/public/reports/navps", args.live,
                                    params={"portfolio_id": 1, "start_date": "2024-09-28T00:00:00.000Z",
                                            "end_date": "2026-09-28T23:59:59.999Z", "page": 1, "size": 1000})
            meta_records.append(meta)
            if len(payload["data"]) != payload["total_count"]:
                raise ValueError("Gohar manager report is paginated/incomplete")
            # Keep the source's local valuation date; do not shift UTC dates.
            rows = [{"date": r["date_time"][:10], "nav": r["redemption_price"],
                     "manager_source_snapshot": meta["sha256"]} for r in payload["data"]]
            report["gohar_unit_change"] = [{k: r.get(k) for k in ["date_time", "redemption_price", "total_unit_count",
                                                                   "total_net_asset_value_with_sell_commission_and_discount"]}
                                            for r in payload["data"] if r["date_time"][:10] in ["2026-09-26", "2026-09-27", "2026-09-28"]]
        else:
            url = "https://iran-kfunds5.ir/Reports/FundNAVList"
            params = {"FromDate": "1403/07/07", "ToDate": "1405/07/06", "BasketId": 1, "page": 1}
            html, meta = request(session, fund, "manager_nav_page1", url, args.live, params=params, as_json=False)
            meta_records.append(meta)
            rows, pages = ganj_page(html, meta["sha256"])
            if pages > 50:
                raise ValueError("Unexpected Ganj pagination; review date filter")
            def fetch_page(number):
                # Follow the page's returned BasketId=0 pagination; validate every
                # row's sole fund-group name before accepting its NAV.
                html, meta = request(requests.Session(), fund, f"manager_nav_page{number}", url, args.live,
                                     params={**params, "BasketId": 0, "page": number}, as_json=False)
                data, _ = ganj_page(html, meta["sha256"])
                return data, meta
            with ThreadPoolExecutor(max_workers=4) as pool:
                for data, meta in pool.map(fetch_page, range(2, pages + 1)):
                    rows.extend(data)
                    meta_records.append(meta)
        original_count = len(rows)
        frame = validate(pd.DataFrame(rows))
        frame = frame.loc[frame.date.between(*report["window"])].copy()
        frame["fund"] = fund
        all_rows.append(frame)
        prices = pd.read_csv(PROJECT / f"data/raw/funds/{fund}/price.csv")
        prices = prices.loc[(prices.trade_volume > 0) & (prices.trade_count > 0) & prices.date.between(*report["window"])]
        saved = pd.read_csv(PROJECT / f"data/raw/funds/{fund}/nav_fipiran.csv").rename(columns={"redemption_nav_irr": "nav"})
        metric, diff = compare(saved, frame, fund, "saved_fipiran_vs_manager", prices, *report["window"])
        all_diff.append(diff)
        entry = {"requests": meta_records, "response_rows": original_count, "valid_dates_in_window": len(frame),
                 "matched_traded_dates": int(prices.date.isin(frame.date).sum()),
                 "traded_dates": len(prices), "saved_fipiran_vs_manager": metric}
        tse = pd.read_csv(PROJECT / f"data/raw/funds/{fund}/nav.csv").rename(columns={"redemption_nav_irr": "nav"})
        metric, diff = compare(tse, frame, fund, "saved_tsetmc_vs_manager", prices, *report["window"])
        all_diff.append(diff)
        entry["saved_tsetmc_vs_manager"] = metric
        report["funds"][fund] = entry
        print(fund, "manager dates", len(frame), "Fipiran conflicts", entry["saved_fipiran_vs_manager"]["different"], flush=True)
    manager_rows = pd.concat(all_rows, ignore_index=True)
    _atomic_csv(manager_rows, OUT / "manager_nav_validation.csv")
    _atomic_csv(pd.concat(all_diff, ignore_index=True), OUT / "manager_disagreements.csv")
    report["trading_validation_counts"] = trading_validation(manager_rows, report["window"])
    (OUT / "manager_audit.json").write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    main()
