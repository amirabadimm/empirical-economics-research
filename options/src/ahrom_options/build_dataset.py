from __future__ import annotations

import csv
import json
import math
from datetime import date
from pathlib import Path

from .common import ROOT, atomic_bytes, atomic_csv, read_archive, today
from .discover_contracts import MASTER_COLUMNS
from .optionbaaz_client import validate_response

PANEL_COLUMNS = ["date", "symbol", "ins_code", "underlying_symbol", "underlying_ins_code",
                 "option_type", "strike", "expiration_date", "option_open", "option_high",
                 "option_low", "option_close", "option_end_price", "volume", "turnover",
                 "open_interest", "iv", "underlying_end_price", "days_to_expiry",
                 "moneyness", "intrinsic_value", "flag_iv_zero", "flag_iv_extreme",
                 "flag_zero_volume", "flag_close_endprice_gap", "flag_intrinsic_violation",
                 "flag_ohlc_inconsistent", "flag_missing_underlying"]


def number(value):
    if value is None or value == "":
        return None
    result = float(value)
    return result if math.isfinite(result) else None


def panel_row(contract: dict, point: dict, underlying_price) -> dict:
    trade_date = date.fromisoformat(str(point["date"]))
    expiry = date.fromisoformat(contract["expiration_date"])
    strike = number(contract["strike"])
    underlying = number(underlying_price)
    close = number(point.get("close"))
    end_price = number(point.get("endPrice"))
    low = number(point.get("low"))
    high = number(point.get("high"))
    opened = number(point.get("open"))
    volume = number(point.get("volume"))
    iv = number(point.get("iv"))
    intrinsic = (max(underlying - strike, 0) if contract["option_type"] == "call"
                 else max(strike - underlying, 0)) if underlying is not None and strike is not None else None
    ohlc = (opened is not None and high is not None and low is not None and close is not None
            and (low > high or (volume is not None and volume > 0
                                 and (opened < low or opened > high or close < low or close > high))))
    return {"date": trade_date.isoformat(), "symbol": contract["symbol"],
            "ins_code": contract["ins_code"], "underlying_symbol": contract["underlying_symbol"],
            "underlying_ins_code": contract["underlying_ins_code"],
            "option_type": contract["option_type"], "strike": contract["strike"],
            "expiration_date": contract["expiration_date"],
            "option_open": point.get("open"), "option_high": point.get("high"),
            "option_low": point.get("low"), "option_close": point.get("close"),
            "option_end_price": point.get("endPrice"), "volume": point.get("volume"),
            "turnover": point.get("turnover"), "open_interest": point.get("openInterest"),
            "iv": point.get("iv"), "underlying_end_price": underlying_price,
            "days_to_expiry": (expiry - trade_date).days,
            "moneyness": underlying / strike if underlying is not None and strike else None,
            "intrinsic_value": intrinsic,
            "flag_iv_zero": iv == 0 if iv is not None else False,
            "flag_iv_extreme": iv > 2 if iv is not None else False,
            "flag_zero_volume": volume == 0 if volume is not None else False,
            "flag_close_endprice_gap": (abs(close - end_price) / max(abs(end_price), 1) > 0.5
                                        if close is not None and end_price is not None else False),
            "flag_intrinsic_violation": (end_price < intrinsic * 0.5
                                         if end_price is not None and intrinsic is not None
                                         and intrinsic > 0 and volume is not None and volume > 0 else False),
            "flag_ohlc_inconsistent": ohlc,
            "flag_missing_underlying": underlying is None}


def build(root: Path = ROOT) -> dict:
    processed = root / "data/processed"
    with (processed / "ahrom_option_contracts.csv").open(encoding="utf-8-sig", newline="") as source:
        contracts = list(csv.DictReader(source))
    manifest_path = processed / "download_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    rows = []
    validation_errors = []
    covered = 0
    for contract in contracts:
        code = contract["ins_code"]
        item = manifest.get(code)
        if not item:
            continue
        try:
            body = read_archive(root / item["archive"])
            errors = validate_response(body, contract)
            if errors:
                validation_errors.append({"ins_code": code, "errors": ";".join(errors),
                                          "archive": item["archive"]})
                continue
            data = body["data"]
            underlying = {}
            for point in data.get("underlyingPoints") or []:
                if point.get("date") in underlying:
                    raise ValueError("duplicate_underlying_date")
                underlying[point["date"]] = point.get("endPrice")
            contract_rows = [panel_row(contract, point, underlying.get(point.get("date")))
                             for point in data["points"]]
            dates = [row["date"] for row in contract_rows]
            if len(dates) != len(set(dates)):
                raise ValueError("duplicate_option_date")
            if dates:
                contract["optionbaaz_first_date"] = min(dates)
                contract["optionbaaz_last_date"] = max(dates)
            rows.extend(contract_rows)
            covered += 1
        except (OSError, ValueError, KeyError, TypeError) as exc:
            validation_errors.append({"ins_code": code, "errors": type(exc).__name__ + ":" + str(exc)[:150],
                                      "archive": item["archive"]})
    rows.sort(key=lambda row: (row["date"], row["ins_code"]))
    atomic_csv(processed / "ahrom_option_contracts.csv", contracts, MASTER_COLUMNS)
    atomic_csv(processed / "ahrom_options_history.csv", rows, PANEL_COLUMNS)
    atomic_csv(processed / "validation_errors.csv", validation_errors,
               ["ins_code", "errors", "archive"])
    parquet_status = "unavailable: pyarrow is not installed"
    try:
        import pandas as pd
        import pyarrow  # noqa: F401
        destination = processed / "ahrom_options_history.parquet"
        temporary = destination.with_suffix(".parquet.tmp")
        pd.DataFrame(rows, columns=PANEL_COLUMNS).to_parquet(temporary, index=False)
        temporary.replace(destination)
        parquet_status = "written"
    except ImportError:
        pass
    flags = {column: {"count": sum(bool(row[column]) for row in rows),
                      "percent": round(100 * sum(bool(row[column]) for row in rows) / len(rows), 2)
                      if rows else 0}
             for column in PANEL_COLUMNS if column.startswith("flag_")}
    download_audit_path = processed / "download_audit.json"
    download_audit = (json.loads(download_audit_path.read_text(encoding="utf-8"))
                      if download_audit_path.exists() else {})
    quality = {"built_on": today(), "contracts_discovered": len(contracts),
               "active": sum(c["status"] == "active" for c in contracts),
               "expired": sum(c["status"] == "expired" for c in contracts),
               "earliest_contract": (min(contracts, key=lambda c: c["expiration_date"])["symbol"]
                                     if contracts else None),
               "latest_contract": (max(contracts, key=lambda c: c["expiration_date"])["symbol"]
                                   if contracts else None),
               "earliest_expiration": min((c["expiration_date"] for c in contracts), default=None),
               "latest_expiration": max((c["expiration_date"] for c in contracts), default=None),
               "earliest_observation": min((r["date"] for r in rows), default=None),
               "latest_observation": max((r["date"] for r in rows), default=None),
               "contracts_with_valid_download": covered,
               "contracts_with_observations": sum(bool(c["optionbaaz_first_date"]) for c in contracts),
               "downloads_attempted": download_audit.get("ever_attempted", download_audit.get("attempted", 0)),
               "downloads_successful": download_audit.get("available", covered),
               "downloads_failed": download_audit.get("failed", 0),
               "panel_rows": len(rows), "flags": flags,
               "validation_error_count": len(validation_errors),
               "parquet": parquet_status,
               "history_limit": "OptionBaaz daily supports only 3m, 6m, 1y; older coverage unverified"}
    atomic_bytes(processed / "quality_report.json", json.dumps(quality, ensure_ascii=False, indent=2).encode())
    return quality
