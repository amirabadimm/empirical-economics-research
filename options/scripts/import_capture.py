"""Import browser captures without changing source evidence; rebuild derived CSVs."""
from __future__ import annotations
import argparse
import csv
import hashlib
import io
import json
import os
from pathlib import Path
import re
import shutil
import tempfile
from decimal import Decimal, InvalidOperation

FIELDS = {
    "last_price": "آخرین قیمت", "strike_price_detail": "قیمت اعمال",
    "break_even": "نقطه سر به سر", "close_price": "قیمت پایانی",
    "trade_value": "ارزش معاملات", "volume": "حجم معاملات",
    "last_trade_jalali": "آخرین معامله", "trade_count": "تعداد معاملات",
    "monthly_mean_volume": "میانگین حجم ماه", "bs_hv": "بلک شولز HV",
    "moneyness": "وضعیت مالی", "expiry_detail": "تاریخ سررسید",
    "bs_wiv_expiry": "بلک شولز W_IV_SE", "contract_size": "اندازه قرارداد",
    "days_remaining": "روز مانده", "bs_wiv": "بلک شولز W_IV",
    "intrinsic_value": "ارزش ذاتی", "time_value": "ارزش زمانی",
    "iv": "IV", "margin_required": "وجه تضمین لازم",
    "minimum_margin": "حداقل وجه تضمین", "delta": "دلتا",
    "leverage": "اهرم", "open_interest": "موقعیت باز",
    "gamma": "گاما", "vega": "وگا", "theta": "تتا",
}
DIGITS = str.maketrans("۰۱۲۳۴۵۶۷۸۹٠١٢٣٤٥٦٧٨٩", "01234567890123456789")
MISSING = {"", "-", "—", "∅"}
TEXT_FIELDS = {"last_trade_jalali", "moneyness", "expiry_detail"}


def number(value):
    value = str(value).translate(DIGITS)
    value = re.sub(r"[\u200e\u200f\u202a-\u202e\u2066-\u2069]", "", value)
    value = value.replace(",", "").replace("٬", "").replace("٫", ".").strip()
    if value in MISSING:
        return ""
    match = re.fullmatch(r"([+-]?\d+(?:\.\d+)?)\s*([KMB])?", value)
    if not match:
        raise ValueError(f"Unrecognized numeric value: {value!r}")
    factor = {None: 1, "K": 1000, "M": 1000000, "B": 1000000000}[match[2]]
    try:
        return format(Decimal(match[1]) * factor, "f")
    except InvalidOperation as exc:
        raise ValueError(value) from exc


def blocks(text):
    # Exclude navigation and Heston's second delta. Source label order is retained.
    text = text.split("معاملات\n", 1)[-1].split("مدل هستون", 1)[0]
    lines = [line.strip() for line in text.splitlines() if line.strip()]
    labels = set(FIELDS.values())
    out = {}
    for index, line in enumerate(lines):
        if line not in labels:
            continue
        following = []
        for nxt in lines[index + 1:]:
            if nxt in labels or nxt in {"ارزش‌گذاری و مشخصات قرارداد", "نوسان، یونانی‌ها و تضمین"}:
                break
            following.append(nxt)
        out[line] = following
    return out


def normalize(contract, record, snapshot):
    result = {"symbol": contract["symbol"], "underlying": "اهرم",
              "option_type": contract["option_type"], "expiry_jalali": contract["expiry_jalali"],
              "contract_status": contract["status"], "strike_price": number(contract["strike"]),
              "detail_availability": "captured" if record else "no_detail_link",
              "source_url": contract.get("url") or "", "snapshot_sha256": snapshot,
              "captured_at_utc": record.get("captured_at", "") if record else "",
              "tsetmc_url": record.get("tsetmc", "") if record else ""}
    data = blocks(record["text"]) if record else {}
    for name, label in FIELDS.items():
        values = data.get(label, [])
        result[name + "_raw"] = " | ".join(values)
        first = values[0] if values else ""
        if name.startswith("bs_"):
            result[name + "_volatility_input"] = number(first)
            result[name + "_price"] = number(values[1]) if len(values) > 1 else ""
        elif name in TEXT_FIELDS:
            result[name] = first
        else:
            result[name] = number(first)
    result["rho"] = ""  # Not exposed in the standard Greek panel; Heston rho is different.
    if not record:
        result["iv_quality"] = "detail_not_available"
    elif contract["status"] == "expired":
        result["iv_quality"] = "expired_snapshot_not_current" if result["iv"] else "expired_iv_not_exposed"
    else:
        result["iv_quality"] = "displayed_numeric" if result["iv"] else "not_exposed_after_wait"
    result["greeks_quality"] = ("expired_not_current" if contract["status"] == "expired"
                                else "displayed_precision") if record else "detail_not_available"
    return result


def orderbook(contract, record, snapshot):
    if not record:
        return []
    marker = "تعداد\nحجم\nقیمت\nقیمت\nحجم\nتعداد\n"
    if marker not in record["text"]:
        return []
    tokens = record["text"].split(marker, 1)[1].splitlines()[:30]
    if len(tokens) != 30:
        raise ValueError("Incomplete visible order book for " + contract["symbol"])
    names = ["bid_count", "bid_volume", "bid_price", "ask_price", "ask_volume", "ask_count"]
    result = []
    for index in range(5):
        row = {"symbol": contract["symbol"], "level": index + 1,
               "contract_status": contract["status"], "snapshot_sha256": snapshot,
               "captured_at_utc": record["captured_at"]}
        for name, token in zip(names, tokens[index * 6:index * 6 + 6]):
            row[name + "_raw"] = token
            row[name] = number(token)
        result.append(row)
    return result


def atomic_write(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(dir=path.parent, delete=False) as handle:
        temp = Path(handle.name)
        handle.write(data)
        handle.flush()
        os.fsync(handle.fileno())
    os.replace(temp, path)


def write_csv(path, rows):
    if not rows:
        return
    fieldnames = list(dict.fromkeys(key for row in rows for key in row))
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)
    atomic_write(path, stream.getvalue().encode("utf-8-sig"))


def import_capture(source, root):
    source, root = Path(source), Path(root)
    completion = json.loads((source / "capture_complete.json").read_text(encoding="utf-8"))
    inventory = json.loads((source / "catalog.json").read_text(encoding="utf-8"))["catalog"]
    files = [source / name for name in ("inventory.json", "catalog.json", "capture_complete.json",
                                      "iv_history.csv", "iv_history_notes.txt")]
    files += sorted((source / "contracts_final").glob("*.json"))
    records = {}
    for path in files:
        if path.parent.name == "contracts_final":
            record = json.loads(path.read_text(encoding="utf-8"))
            if record["symbol"] in records:
                raise ValueError("Duplicate detail capture")
            records[record["symbol"]] = record
    symbols = [item["symbol"] for item in inventory]
    linked = {item["symbol"] for item in inventory if item.get("url")}
    if len(symbols) != len(set(symbols)) or set(records) != linked:
        raise ValueError("Catalogue/detail coverage mismatch")
    if len(records) != completion["captured_contracts"]:
        raise ValueError("Capture completion count mismatch")
    manifest = {str(p.relative_to(source)).replace("\\", "/"): hashlib.sha256(p.read_bytes()).hexdigest()
                for p in files}
    snapshot = hashlib.sha256(json.dumps(manifest, sort_keys=True).encode()).hexdigest()
    archive = root / "data/raw/optionbaaz" / snapshot
    if archive.exists():
        for relative, digest in manifest.items():
            if hashlib.sha256((archive / relative).read_bytes()).hexdigest() != digest:
                raise ValueError("Existing raw archive changed: " + relative)
    else:
        archive.parent.mkdir(parents=True, exist_ok=True)
        staging = Path(tempfile.mkdtemp(prefix=".import-", dir=archive.parent))
        try:
            for path in files:
                target = staging / path.relative_to(source)
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(path, target)
            (staging / "manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
            staging.rename(archive)
        except BaseException:
            # Keep partial evidence for diagnosis; never remove a source archive.
            raise
    rows = [normalize(item, records.get(item["symbol"]), snapshot) for item in inventory]
    rows.sort(key=lambda row: (row["expiry_jalali"], row["option_type"], Decimal(row["strike_price"])))
    books = [row for item in inventory for row in orderbook(item, records.get(item["symbol"]), snapshot)]
    errors = []
    for row in rows:
        if row["expiry_detail"] and row["expiry_detail"] != row["expiry_jalali"]:
            errors.append("Expiry mismatch: " + row["symbol"])
        if row["strike_price_detail"] and Decimal(row["strike_price_detail"]) != Decimal(row["strike_price"]):
            errors.append("Strike mismatch: " + row["symbol"])
    if errors:
        raise ValueError("; ".join(errors))
    out = root / "data/processed/analysis" / snapshot
    write_csv(out / "contracts.csv", rows)
    write_csv(out / "calls.csv", [r for r in rows if r["option_type"] == "call"])
    write_csv(out / "puts.csv", [r for r in rows if r["option_type"] == "put"])
    write_csv(out / "active_contracts.csv", [r for r in rows if r["contract_status"] == "active"])
    write_csv(out / "orderbook.csv", books)
    atomic_write(out / "underlying_iv_history.csv", (archive / "iv_history.csv").read_bytes())
    summary = {"snapshot_sha256": snapshot, "catalogue_contracts": len(rows),
               "calls": sum(r["option_type"] == "call" for r in rows),
               "puts": sum(r["option_type"] == "put" for r in rows),
               "active": sum(r["contract_status"] == "active" for r in rows),
               "expired": sum(r["contract_status"] == "expired" for r in rows),
               "detail_pages": len(records), "catalogue_only": len(rows)-len(records),
               "expiries": sorted(set(r["expiry_jalali"] for r in rows)),
               "active_with_iv": sum(r["contract_status"] == "active" and bool(r["iv"]) for r in rows),
               "active_missing_iv": [r["symbol"] for r in rows if r["contract_status"] == "active" and not r["iv"]],
               "expired_with_displayed_iv": [r["symbol"] for r in rows if r["contract_status"] == "expired" and r["iv"]],
               "orderbook_rows": len(books), "validation_errors": errors,
               "derived_directory": str(out), "raw_directory": str(archive)}
    atomic_write(out / "validation.json", json.dumps(summary, ensure_ascii=False, indent=2).encode())
    atomic_write(root / "data/processed/analysis/latest.json", json.dumps(summary, ensure_ascii=False, indent=2).encode())
    return summary


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("capture", type=Path)
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    print(json.dumps(import_capture(args.capture, args.root), ensure_ascii=True, indent=2))
