"""Read-only connectivity and schema probe for copper data sources.

This diagnostic does not create or modify any dataset. It tests candidate
public endpoints, searches for copper-related rows, and prints a compact report.
"""

from __future__ import annotations

import argparse
import json
import socket
import ssl
import sys
import time
from dataclasses import dataclass
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import quote, urlencode
from urllib.request import Request, urlopen


IME_CERTIFICATE_URL = (
    "https://www.ime.co.ir/subsystems/ime/bazaremali/bazaremalidata.ashx"
)
IME_PHYSICAL_URL = (
    "https://www.ime.co.ir/subsystems/ime/services/home/"
    "imedata.asmx/GetAmareMoamelatList"
)
TSETMC_SEARCH_URL = "https://cdn.tsetmc.com/api/Instrument/GetInstrumentSearch/{}"


@dataclass
class ProbeResult:
    name: str
    ok: bool
    elapsed_seconds: float
    status: int | None = None
    detail: str = ""


def request_json(
    url: str,
    timeout: int,
    *,
    method: str = "GET",
    payload: dict[str, Any] | None = None,
    referer: str | None = None,
) -> tuple[int, Any]:
    body = json.dumps(payload).encode("utf-8") if payload is not None else None
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 Chrome/124.0 Safari/537.36"
        ),
        "Accept": "application/json, text/javascript, text/plain, */*",
        "Accept-Language": "fa-IR,fa;q=0.9,en;q=0.8",
        "Connection": "close",
    }
    if payload is not None:
        headers["Content-Type"] = "application/json; charset=utf-8"
        headers["X-Requested-With"] = "XMLHttpRequest"
    if referer:
        headers["Referer"] = referer

    request = Request(url, data=body, headers=headers, method=method)
    context = ssl.create_default_context()
    with urlopen(request, timeout=timeout, context=context) as response:
        raw = response.read()
        return response.status, json.loads(raw.decode("utf-8-sig"))


def flatten_values(value: Any) -> str:
    if isinstance(value, dict):
        return " ".join(flatten_values(item) for item in value.values())
    if isinstance(value, list):
        return " ".join(flatten_values(item) for item in value)
    return str(value)


def contains_copper(record: Any) -> bool:
    text = flatten_values(record).casefold()
    terms = ("coppercthd", "cd1cop0001", "مس کاتد", "کاتد مس")
    return any(term.casefold() in text for term in terms)


def unpack_rows(response: Any) -> list[dict[str, Any]]:
    if isinstance(response, dict) and isinstance(response.get("rows"), list):
        return response["rows"]
    if isinstance(response, dict) and "d" in response:
        nested = response["d"]
        if isinstance(nested, str):
            nested = json.loads(nested)
        return nested if isinstance(nested, list) else []
    if isinstance(response, dict):
        for key in ("instrumentSearch", "data", "Data", "result"):
            if isinstance(response.get(key), list):
                return response[key]
    return response if isinstance(response, list) else []


def compact_record(record: dict[str, Any]) -> dict[str, Any]:
    preferred = (
        "insCode",
        "instrumentID",
        "lVal18AFC",
        "lVal30",
        "Namad",
        "LVal18AFC",
        "NamadDescription",
        "DT",
        "DT_En",
        "PClosing",
        "PDrCotVal",
        "QTotTran5J",
        "QTotCap",
        "ZTotTran",
        "GoodsName",
        "Symbol",
        "ProducerName",
        "ContractType",
        "ClosePrice",
        "TransactionValue",
        "Date",
        "Unit",
    )
    selected = {key: record[key] for key in preferred if key in record}
    return selected or {key: record[key] for key in list(record)[:12]}


def run_probe(name: str, operation: Any) -> ProbeResult:
    started = time.monotonic()
    try:
        status, response = operation()
        rows = unpack_rows(response)
        matches = [row for row in rows if isinstance(row, dict) and contains_copper(row)]
        elapsed = time.monotonic() - started
        print(f"\n[{name}] HTTP {status}; rows={len(rows)}; copper_matches={len(matches)}")
        if rows and isinstance(rows[0], dict):
            print("response_keys:", sorted(rows[0].keys()))
        for record in matches[:3]:
            print("match:", json.dumps(compact_record(record), ensure_ascii=False))
        return ProbeResult(name, True, elapsed, status, f"{len(matches)} copper matches")
    except HTTPError as exc:
        detail = f"HTTP {exc.code}: {exc.reason}"
    except (URLError, TimeoutError, socket.timeout, ssl.SSLError) as exc:
        detail = f"{type(exc).__name__}: {exc}"
    except (json.JSONDecodeError, ValueError, TypeError) as exc:
        detail = f"response/schema error: {exc}"
    except Exception as exc:  # The probe must report unexpected source behavior.
        detail = f"{type(exc).__name__}: {exc}"
    elapsed = time.monotonic() - started
    print(f"\n[{name}] FAILED after {elapsed:.1f}s — {detail}")
    return ProbeResult(name, False, elapsed, detail=detail)


def main() -> int:
    # Keep Persian symbol names printable on Windows consoles with legacy code pages.
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--timeout", type=int, default=30, help="timeout per endpoint")
    parser.add_argument("--from-date", default="1404/07/28", help="Jalali YYYY/MM/DD")
    parser.add_argument("--to-date", default="1404/08/10", help="Jalali YYYY/MM/DD")
    args = parser.parse_args()

    cert_query = urlencode(
        {
            "f": args.from_date,
            "t": args.to_date,
            "c": 1,
            "ot": 0,
            "lang": 8,
            "order": "asc",
        }
    )
    physical_payload = {
        "Language": 8,
        "fari": False,
        "GregorianFromDate": args.from_date,
        "GregorianToDate": args.to_date,
        "MainCat": 0,
        "Cat": 0,
        "SubCat": 0,
        "Producer": 0,
    }

    probes = [
        (
            "IME certificate",
            lambda: request_json(
                f"{IME_CERTIFICATE_URL}?{cert_query}",
                args.timeout,
                referer="https://www.ime.co.ir/standard-transactions.html",
            ),
        ),
        (
            "IME physical",
            lambda: request_json(
                IME_PHYSICAL_URL,
                args.timeout,
                method="POST",
                payload=physical_payload,
                referer="https://www.ime.co.ir/offer-stat.html",
            ),
        ),
    ]
    for query in ("CopperCthd", "CD1COP0001", "مس کاتد"):
        probes.append(
            (
                f"TSETMC search: {query}",
                lambda query=query: request_json(
                    TSETMC_SEARCH_URL.format(quote(query, safe="")), args.timeout
                ),
            )
        )

    print("Read-only source probe; no files will be written.")
    results = [run_probe(name, operation) for name, operation in probes]
    print("\nSummary")
    for result in results:
        outcome = "OK" if result.ok else "FAILED"
        print(f"- {result.name}: {outcome} ({result.elapsed_seconds:.1f}s) {result.detail}")
    return 0 if any(result.ok for result in results) else 2


if __name__ == "__main__":
    sys.exit(main())
