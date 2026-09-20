from __future__ import annotations

import json
import os
from pathlib import Path

import requests

from .common import (ROOT, UNDERLYING_CODE, RawJson, archive_json, atomic_bytes,
                     fetch_json, read_archive, session, today)

URL = "https://api.optionbaaz.ir/market-history/daily"
PERIOD = "1y"


def validate_response(body: dict, contract: dict) -> list[str]:
    errors = []
    if body.get("status") != "success" or not isinstance(body.get("data"), dict):
        return ["api_status_not_success"]
    data = body["data"]
    if str(data.get("symbolId")) != str(contract["ins_code"]):
        errors.append("symbol_id_mismatch")
    underlying = data.get("underlyingLast") or {}
    if underlying.get("symbolId") is not None and str(underlying["symbolId"]) != UNDERLYING_CODE:
        errors.append("underlying_id_mismatch")
    if str(data.get("namad") or "") != str(contract["symbol"]):
        errors.append("symbol_mismatch")
    meta = data.get("optionMeta") or {}
    if meta.get("strikePrice") is not None:
        try:
            if float(meta["strikePrice"]) != float(contract["strike"]):
                errors.append("strike_mismatch")
        except (ValueError, TypeError):
            errors.append("strike_invalid")
    if meta.get("contractType") is not None and meta["contractType"] != contract["option_type"]:
        errors.append("option_type_mismatch")
    if data.get("period") != PERIOD:
        errors.append("period_mismatch")
    if not isinstance(data.get("points"), list) or not isinstance(data.get("underlyingPoints") or [], list):
        errors.append("points_not_lists")
    return errors


def collect(contracts: list[dict], root: Path = ROOT, *, refresh: bool = False,
            delay: float = 0.35) -> dict:
    token = os.environ["OPTIONBAAZ_ACCESS_TOKEN"].strip()
    if not token:
        raise ValueError("OPTIONBAAZ_ACCESS_TOKEN is empty")
    manifest_path = root / "data/processed/download_manifest.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {}
    audit_path = root / "data/processed/download_audit.json"
    prior_audit = json.loads(audit_path.read_text(encoding="utf-8")) if audit_path.exists() else {}
    known_404 = {item["ins_code"]: item for item in prior_audit.get("failures", [])
                 if item.get("http_status") == 404}
    client = session()
    stats = {"attempted": 0, "successful": 0, "cached": 0, "cached_404": 0, "failed": 0,
             "failures": [], "validation_errors": []}
    for contract in contracts:
        code = str(contract["ins_code"])
        prior = manifest.get(code)
        if prior and not refresh:
            archive = root / prior["archive"]
            if archive.is_file():
                try:
                    body = read_archive(archive)
                    errors = validate_response(body, contract)
                    if not errors:
                        if not prior.get("valid"):
                            prior["valid"] = True
                            prior["errors"] = []
                            atomic_bytes(manifest_path,
                                         json.dumps(manifest, ensure_ascii=False, indent=2).encode())
                        stats["cached"] += 1
                        continue
                    stats["validation_errors"].append({"ins_code": code, "errors": errors,
                                                       "archive": prior["archive"]})
                except (OSError, ValueError):
                    pass
        if not refresh and code in known_404 and not prior:
            stats["cached_404"] += 1
            stats["failed"] += 1
            stats["failures"].append(known_404[code])
            continue
        stats["attempted"] += 1
        try:
            body = fetch_json(client, URL, params={"symbolId": code, "period": PERIOD},
                              cookies={"access_token": token}, delay=delay)
            archive = archive_json(root / "data/raw/optionbaaz/contracts" / code, body)
            relative = str(archive.relative_to(root))
            errors = validate_response(body, contract)
            manifest[code] = {"archive": relative, "captured_on": today(),
                              "period": PERIOD, "valid": not errors, "errors": errors}
            atomic_bytes(manifest_path, json.dumps(manifest, ensure_ascii=False, indent=2).encode())
            if errors:
                stats["validation_errors"].append({"ins_code": code, "errors": errors,
                                                   "archive": relative})
            else:
                stats["successful"] += 1
        except Exception as exc:
            stats["failed"] += 1
            failure = {"ins_code": code, "error_type": type(exc).__name__,
                       "message": str(exc)[:200]}
            if isinstance(exc, requests.HTTPError) and exc.response is not None:
                failure["http_status"] = exc.response.status_code
                try:
                    error_body = exc.response.json()
                    if isinstance(error_body, dict):
                        archive = archive_json(root / "data/raw/optionbaaz/errors" / code,
                                               RawJson(error_body, exc.response.content))
                        failure["archive"] = str(archive.relative_to(root))
                except ValueError:
                    pass
            stats["failures"].append(failure)
        if (stats["attempted"] % 25) == 0:
            atomic_bytes(audit_path,
                         json.dumps(stats, ensure_ascii=False, indent=2).encode())
            print(f"OptionBaaz attempts: {stats['attempted']}; successful: {stats['successful']}; "
                  f"failed: {stats['failed']}", flush=True)
    stats["ever_attempted"] = len(set(manifest) | {item["ins_code"] for item in stats["failures"]})
    stats["available"] = sum(bool(item.get("valid")) for item in manifest.values())
    atomic_bytes(audit_path,
                 json.dumps(stats, ensure_ascii=False, indent=2).encode())
    return stats
