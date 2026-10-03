"""Replace five disposable live readings; rank only against completed daily history."""
from __future__ import annotations

import calendar
from concurrent.futures import ThreadPoolExecutor
from datetime import date, datetime, time, timedelta, timezone
import json
import math
import os
from pathlib import Path
from zoneinfo import ZoneInfo

import requests

from load_gold import FUNDS, METHOD

PROJECT = Path(__file__).resolve().parents[1]
TEHRAN = ZoneInfo("Asia/Tehran")


def is_market_time(now):
    clock = now.astimezone(TEHRAN).time().replace(tzinfo=None)
    return time(12) <= clock < time(18, 1)


def source_time(day, clock):
    return datetime.strptime(f"{int(day):08d}{int(clock):06d}", "%Y%m%d%H%M%S").replace(tzinfo=TEHRAN)


def evaluate(price, nav, ins_code, now):
    if str(nav["insCode"]) != str(ins_code):
        raise ValueError("NAV instrument identity mismatch")
    # The price endpoint currently returns insCode='0'; route identity is configured.
    if str(price.get("insCode", "0")) not in ("0", str(ins_code)):
        raise ValueError("Price instrument identity mismatch")
    last, redemption = float(price["pDrCotVal"]), float(nav["pRedTran"])
    if not all(math.isfinite(x) and x > 0 for x in (last, redemption)):
        raise ValueError("Nonpositive or nonfinite current price/NAV")
    price_at = source_time(price["dEven"], price["hEven"])
    nav_at = source_time(nav["deven"], nav["hEven"])
    ages = [(now - t).total_seconds() for t in (price_at, nav_at)]
    fresh = (all(-120 <= age <= 1200 for age in ages)
             and price_at.date() == nav_at.date() == now.astimezone(TEHRAN).date()
             and abs((price_at - nav_at).total_seconds()) <= 900
             and float(price.get("zTotTran", 0)) > 0)
    return {
        "price_at": price_at, "nav_at": nav_at, "last": last, "nav": redemption,
        "bubble": 100 * (last / redemption - 1) if fresh else None,
        "status": "fresh" if fresh else "stale_or_unaligned",
    }


def rank_daily(values, bubble):
    if not values or bubble is None:
        return None, None
    percentile = 100 * sum(float(x) <= bubble for x in values) / len(values)
    return percentile, max(1, min(10, math.ceil(round(percentile, 8) / 10)))


def months_before(day, months):
    index = day.year * 12 + day.month - 1 - months
    year, month = divmod(index, 12)
    month += 1
    return day.replace(year=year, month=month, day=min(day.day, calendar.monthrange(year, month)[1]))


def reference_ranks(history, bubble, cutoff):
    # All samples precede today's date; the disposable observation is never inserted.
    history = [(day, float(value)) for day, value in history if day < cutoff]
    year = [v for d, v in history if d >= months_before(cutoff, 12)]
    six = [v for d, v in history if d >= months_before(cutoff, 6)]
    two_year = [v for d, v in history if d >= max(months_before(cutoff, 24), date(2024, 1, 1))]
    yp, yd = rank_daily(year, bubble)
    sp, sd = rank_daily(six, bubble)
    weights = [2 ** (-(cutoff - d).days / 90) for d, _ in history]
    total = sum(weights)
    wp = 100 * sum(w for w, (_, v) in zip(weights, history) if v <= bubble) / total if total and bubble is not None else None
    wd = max(1, min(10, math.ceil(round(wp, 8) / 10))) if wp is not None else None
    effective = total ** 2 / sum(w * w for w in weights) if total else None
    tp, td = rank_daily(two_year, bubble)
    return yp, yd, len(year), sp, sd, len(six), wp, wd, len(history), effective, tp, td, len(two_year)


def fetch_fund(item):
    fund, cfg = item
    base = "https://cdn.tsetmc.com/api/"
    try:
        with requests.Session() as session:
            p = session.get(base + f"ClosingPrice/GetClosingPriceInfo/{cfg['ins_code']}", timeout=25)
            p.raise_for_status()
            n = session.get(base + f"Fund/GetETFByInsCode/{cfg['ins_code']}", timeout=25)
            n.raise_for_status()
        price, nav = p.json()["closingPriceInfo"], n.json()["etf"]
        now = datetime.now(timezone.utc)
        return fund, now, evaluate(price, nav, cfg["ins_code"], now), price, nav, None
    except Exception as exc:
        return fund, datetime.now(timezone.utc), None, None, None, type(exc).__name__


def main():
    import psycopg
    from psycopg.types.json import Jsonb
    cfg = json.loads((PROJECT / "config/funds.json").read_text(encoding="utf-8"))
    with psycopg.connect(os.environ["GOLD_DATABASE_URL"]) as conn:
        # Hold the transaction lock during retrieval, preventing overlapping refreshes.
        with conn.cursor() as cur:
            cur.execute("SELECT pg_try_advisory_xact_lock(hashtext('gold_live_v1'))")
            if not cur.fetchone()[0]:
                print("Live refresh already running")
                return
            cur.execute("DELETE FROM research.gold_live_state WHERE expires_at <= now()")
            if not is_market_time(datetime.now(timezone.utc)):
                print("Outside 12:00-18:00 Tehran polling window; no quote requests")
                return
            with ThreadPoolExecutor(max_workers=5) as pool:
                readings = list(pool.map(fetch_fund, [(f, cfg[f]) for f in FUNDS]))
            for fund, now, reading, price, nav, error in readings:
                cur.execute("SELECT instrument_id FROM research.instruments WHERE instrument_key=%s", (fund,))
                instrument_id = cur.fetchone()[0]
                cutoff = now.astimezone(TEHRAN).date()
                cur.execute("""SELECT observation_date, bubble_pct FROM research.bubble_observations
                    WHERE instrument_id=%s AND method_key=%s
                    AND observation_date < %s ORDER BY observation_date""",
                    (instrument_id, METHOD, cutoff))
                history = cur.fetchall()
                r = reading or dict(price_at=None, nav_at=None, last=None, nav=None, bubble=None, status="fetch_error")
                ranks = reference_ranks(history, r["bubble"], cutoff)
                if r["status"] == "fresh" and not history:
                    r["status"] = "no_daily_reference"
                cur.execute("""INSERT INTO research.gold_live_state
                    (instrument_id,retrieved_at,expires_at,price_source_at,nav_source_at,
                     last_price_irr,redemption_nav_irr,bubble_pct,year_percentile,year_decile,year_count,
                     six_month_percentile,six_month_decile,six_month_count,weighted_percentile,weighted_decile,
                     full_history_count,weighted_effective_count,two_year_percentile,two_year_decile,
                     two_year_count,reference_last_date,
                     status,detail,price_payload,nav_payload)
                    VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
                    ON CONFLICT (instrument_id) DO UPDATE SET
                     retrieved_at=EXCLUDED.retrieved_at,expires_at=EXCLUDED.expires_at,
                     price_source_at=EXCLUDED.price_source_at,nav_source_at=EXCLUDED.nav_source_at,
                     last_price_irr=EXCLUDED.last_price_irr,redemption_nav_irr=EXCLUDED.redemption_nav_irr,
                     bubble_pct=EXCLUDED.bubble_pct,year_percentile=EXCLUDED.year_percentile,
                     year_decile=EXCLUDED.year_decile,year_count=EXCLUDED.year_count,
                     six_month_percentile=EXCLUDED.six_month_percentile,six_month_decile=EXCLUDED.six_month_decile,
                     six_month_count=EXCLUDED.six_month_count,weighted_percentile=EXCLUDED.weighted_percentile,
                     weighted_decile=EXCLUDED.weighted_decile,full_history_count=EXCLUDED.full_history_count,
                     weighted_effective_count=EXCLUDED.weighted_effective_count,
                     two_year_percentile=EXCLUDED.two_year_percentile,two_year_decile=EXCLUDED.two_year_decile,
                     two_year_count=EXCLUDED.two_year_count,
                     reference_last_date=EXCLUDED.reference_last_date,status=EXCLUDED.status,
                     detail=EXCLUDED.detail,price_payload=EXCLUDED.price_payload,nav_payload=EXCLUDED.nav_payload
                    """, (instrument_id, now, now + timedelta(hours=24), r["price_at"], r["nav_at"],
                          r["last"], r["nav"], r["bubble"], *ranks, history[-1][0] if history else None,
                          r["status"], error, Jsonb(price) if price else None, Jsonb(nav) if nav else None))
                print(f"{fund}: {r['status']}; daily reference={len(history)}")


if __name__ == "__main__":
    main()
