from __future__ import annotations

import json
import os
import time
from pathlib import Path

from .common import ROOT, RawJson, archive_json, atomic_bytes, session, today
from .optionbaaz_client import URL

PERIODS = ("1m", "3m", "6m", "1y", "2y", "3y", "5y", "max", "all")
SAMPLES = ("242237343005473", "7693632359685850")


def probe(root: Path = ROOT, *, delay: float = 0.25) -> list[dict]:
    token = os.environ["OPTIONBAAZ_ACCESS_TOKEN"].strip()
    client = session()
    rows = []
    for code in SAMPLES:
        for period in PERIODS:
            try:
                response = client.get(URL, params={"symbolId": code, "period": period},
                                      cookies={"access_token": token}, timeout=(10, 30))
                body = response.json()
                archive = archive_json(root / "data/raw/optionbaaz/period_probe" / code / period,
                                       RawJson(body, response.content))
                data = body.get("data") or {}
                points = data.get("points") or []
                dates = sorted(str(point["date"]) for point in points if point.get("date"))
                rows.append({"ins_code": code, "requested_period": period,
                             "http_status": response.status_code, "api_status": body.get("status"),
                             "returned_period": data.get("period"), "observations": len(points),
                             "first_date": dates[0] if dates else None,
                             "last_date": dates[-1] if dates else None,
                             "message": body.get("message"), "archive": str(archive.relative_to(root))})
            except Exception as exc:
                rows.append({"ins_code": code, "requested_period": period,
                             "error_type": type(exc).__name__})
            finally:
                time.sleep(delay)
    atomic_bytes(root / "data/processed/period_probe.json",
                 json.dumps({"date": today(), "results": rows}, ensure_ascii=False, indent=2).encode())
    return rows
