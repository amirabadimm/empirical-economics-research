"""Reusable incremental collector for the official IME physical-market API."""

from __future__ import annotations

import csv
import gzip
import hashlib
import json
import os
import shutil
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import date, datetime, timezone
from pathlib import Path
from typing import Any, Callable, Iterable


API_URL = "https://www.ime.co.ir/subsystems/ime/services/home/imedata.asmx/GetAmareMoamelatList"
LANDING_URL = "https://www.ime.co.ir/offer-stat.html"
FIRST_JALALI_MONTH = (1386, 1)
SOURCE_COLUMNS = [
    "GoodsName",
    "Symbol",
    "ProducerName",
    "ContractType",
    "MinPrice",
    "Price",
    "MaxPrice",
    "arze",
    "ArzeBasePrice",
    "arzeMinPrice",
    "taghaza",
    "taghazavoroudi",
    "taghazaMaxPrice",
    "Quantity",
    "TotalPrice",
    "date",
    "DeliveryDate",
    "Warehouse",
    "ArzehKonandeh",
    "SettlementDate",
    "Category",
    "xTalarReportPK",
    "bArzehRadifTarSarresid",
    "cBrokerSpcName",
    "ModeDescription",
    "MethodDescription",
    "MinPrice1",
    "Price1",
    "Currency",
    "Unit",
    "arzehPk",
    "Talar",
    "PacketName",
    "Tasvieh",
]
RAW_COLUMNS = SOURCE_COLUMNS + ["fetched_at_utc", "source_url"]
WORKSPACE_ROOT = Path(__file__).resolve().parents[2]
SHARED_SNAPSHOT_DIR = WORKSPACE_ROOT / "shared" / "data" / "raw" / "ime" / "physical"


@dataclass(frozen=True)
class PhysicalCollectorConfig:
    project_dir: Path
    output_filename: str
    snapshot_prefix: str
    target_label: str
    row_filter: Callable[[dict[str, Any]], bool]
    shared_snapshot_dir: Path = SHARED_SNAPSHOT_DIR


def normalize_fa(value: Any) -> str:
    return str(value or "").replace("ي", "ی").replace("ك", "ک").strip()


def jalali_to_gregorian(jy: int, jm: int, jd: int) -> tuple[int, int, int]:
    jy += 1595
    days = -355668 + 365 * jy + (jy // 33) * 8 + ((jy % 33 + 3) // 4) + jd
    days += (jm - 1) * 31 if jm < 7 else 186 + (jm - 7) * 30
    gy = 400 * (days // 146097)
    days %= 146097
    if days > 36524:
        days -= 1
        gy += 100 * (days // 36524)
        days %= 36524
        if days >= 365:
            days += 1
    gy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        gy += (days - 1) // 365
        days = (days - 1) % 365
    gd = days + 1
    leap = gy % 4 == 0 and (gy % 100 != 0 or gy % 400 == 0)
    month_days = [31, 29 if leap else 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]
    gm = 1
    for length in month_days:
        if gd <= length:
            break
        gd -= length
        gm += 1
    return gy, gm, gd


def gregorian_to_jalali(gy: int, gm: int, gd: int) -> tuple[int, int, int]:
    offsets = [0, 31, 59, 90, 120, 151, 181, 212, 243, 273, 304, 334]
    gy2 = gy + 1 if gm > 2 else gy
    days = 355666 + 365 * gy + (gy2 + 3) // 4 - (gy2 + 99) // 100
    days += (gy2 + 399) // 400 + gd + offsets[gm - 1]
    jy = -1595 + 33 * (days // 12053)
    days %= 12053
    jy += 4 * (days // 1461)
    days %= 1461
    if days > 365:
        jy += (days - 1) // 365
        days = (days - 1) % 365
    if days < 186:
        return jy, 1 + days // 31, 1 + days % 31
    return jy, 7 + (days - 186) // 30, 1 + (days - 186) % 30


def month_end(year: int, month: int) -> int:
    if month <= 6:
        return 31
    if month <= 11:
        return 30
    g1 = jalali_to_gregorian(year, 12, 29)
    g2 = jalali_to_gregorian(year + 1, 1, 1)
    return 30 if (date(*g2) - date(*g1)).days == 2 else 29


def iter_months(start: tuple[int, int], end: tuple[int, int]):
    year, month = start
    while (year, month) <= end:
        yield year, month
        year, month = (year + 1, 1) if month == 12 else (year, month + 1)


def fetch_rows_requests(
    payload: dict[str, Any], timeout: int
) -> tuple[bytes, list[dict[str, Any]]]:
    import requests

    session = requests.Session()
    session.headers.update({"User-Agent": "Mozilla/5.0"})
    warmup = session.get(LANDING_URL, timeout=min(timeout, 30))
    warmup.raise_for_status()
    response = session.post(
        API_URL,
        json=payload,
        headers={
            "Origin": "https://www.ime.co.ir",
            "Referer": LANDING_URL,
            "X-Requested-With": "XMLHttpRequest",
        },
        timeout=timeout,
    )
    response.raise_for_status()
    raw = response.content
    outer = json.loads(raw.decode("utf-8-sig"))
    rows = json.loads(outer["d"])
    if not isinstance(rows, list):
        raise ValueError("decoded field d is not a list")
    return raw, rows


def fetch_rows(
    payload: dict[str, Any], timeout: int, retries: int
) -> tuple[bytes, list[dict[str, Any]]]:
    if os.environ.get("IME_HTTP_TRANSPORT", "").lower() == "requests":
        return fetch_rows_requests(payload, timeout)
    curl = shutil.which("curl.exe") or shutil.which("curl")
    if not curl:
        raise RuntimeError("curl was not found in PATH")
    encoded = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    last_error = ""
    for attempt in range(1, retries + 1):
        with tempfile.TemporaryDirectory(prefix="ime_physical_") as temp_dir:
            cookie = str(Path(temp_dir) / "cookies.txt")
            common = [
                curl,
                "-4",
                "--tlsv1.2",
                "--silent",
                "--show-error",
                "--connect-timeout",
                str(min(timeout, 30)),
                "--max-time",
                str(timeout),
            ]
            warmup = subprocess.run(
                common + ["--cookie-jar", cookie, LANDING_URL],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.PIPE,
                check=False,
            )
            if warmup.returncode != 0:
                last_error = warmup.stderr.decode("utf-8", errors="replace").strip()
                continue
            command = common + [
                "--cookie",
                cookie,
                "--header",
                "User-Agent: Mozilla/5.0",
                "--header",
                "Origin: https://www.ime.co.ir",
                "--header",
                f"Referer: {LANDING_URL}",
                "--header",
                "X-Requested-With: XMLHttpRequest",
                "--header",
                "Content-Type: application/json; charset=utf-8",
                "--data-binary",
                "@-",
                API_URL,
            ]
            result = subprocess.run(
                command, input=encoded, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False
            )
        if result.returncode == 0:
            try:
                outer = json.loads(result.stdout.decode("utf-8-sig"))
                rows = json.loads(outer["d"])
                if not isinstance(rows, list):
                    raise ValueError("decoded field d is not a list")
                return result.stdout, rows
            except (json.JSONDecodeError, KeyError, TypeError, ValueError) as exc:
                last_error = f"unexpected response: {exc}; prefix={result.stdout[:160]!r}"
        else:
            last_error = result.stderr.decode("utf-8", errors="replace").strip()
        if attempt < retries:
            time.sleep(2 ** (attempt - 1))
    # Windows Schannel can exhaust or lose its client credential context during
    # long month-by-month runs. Keep the source and payload unchanged, but fall
    # back to Python's HTTPS stack instead of discarding a long collection.
    try:
        return fetch_rows_requests(payload, timeout)
    except Exception as exc:
        raise RuntimeError(
            f"IME request failed via curl ({last_error}) and requests fallback ({exc})"
        ) from exc


def validate_selected(rows: Iterable[dict[str, Any]], config: PhysicalCollectorConfig) -> None:
    for row in rows:
        missing = [field for field in SOURCE_COLUMNS if field not in row]
        if missing:
            raise ValueError(f"IME physical schema changed; missing fields: {missing}")
        if not config.row_filter(row):
            raise ValueError(f"out-of-scope row passed filter: {row.get('GoodsName')!r}")


def read_existing(path: Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames != RAW_COLUMNS:
            raise ValueError(f"Unexpected columns in {path}: {reader.fieldnames}")
        return list(reader)


def write_csv_atomic(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=RAW_COLUMNS, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(
            sorted(
                rows,
                key=lambda r: (
                    str(r.get("date")),
                    str(r.get("Symbol")),
                    str(r.get("xTalarReportPK")),
                    str(r.get("ContractType")),
                ),
            )
        )
    temporary.replace(path)


def archive_market_response(
    raw_response: bytes,
    payload: dict[str, Any],
    fetched_at: str,
    year: int,
    month: int,
    snapshot_dir: Path = SHARED_SNAPSHOT_DIR,
) -> Path:
    """Archive a full-market response once, keyed by its immutable source bytes."""
    digest = hashlib.sha256(raw_response).hexdigest()
    path = snapshot_dir / f"ime_physical_{year:04d}-{month:02d}_{digest}.json.gz"
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    archive = {
        "request": payload,
        "fetched_at_utc": fetched_at,
        "source_url": API_URL,
        "response_sha256": digest,
        "response_utf8": raw_response.decode("utf-8-sig"),
    }
    try:
        with path.open("xb") as binary_handle:
            with gzip.GzipFile(fileobj=binary_handle, mode="wb", mtime=0) as gzip_handle:
                gzip_handle.write(json.dumps(archive, ensure_ascii=False).encode("utf-8"))
    except FileExistsError:
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            existing = json.load(handle)
        if existing.get("response_sha256") != digest:
            raise ValueError(f"Shared IME snapshot hash collision or corruption: {path}")
    return path


def available_snapshots(config: PhysicalCollectorConfig) -> list[Path]:
    """Return shared snapshots plus frozen project-local legacy snapshots."""
    legacy_dir = config.project_dir / "data" / "raw" / "physical" / "api_snapshots"
    return sorted(
        [
            *config.shared_snapshot_dir.glob("ime_physical_*.json.gz"),
            *legacy_dir.glob(f"{config.snapshot_prefix}_*.json.gz"),
        ]
    )


def rebuild_from_snapshots(config: PhysicalCollectorConfig) -> None:
    """Rebuild the canonical filtered CSV from the newest snapshot per month."""
    raw_dir = config.project_dir / "data" / "raw" / "physical"
    csv_path = raw_dir / config.output_filename
    newest: dict[str, tuple[str, Path]] = {}
    for path in available_snapshots(config):
        parts = path.name.split("_")
        if len(parts) < 3:
            continue
        if path.name.startswith("ime_physical_"):
            month = parts[2]
            with gzip.open(path, "rt", encoding="utf-8") as handle:
                archive = json.load(handle)
            fetched_at = str(archive.get("fetched_at_utc") or "")
        else:
            month = parts[1]
            fetched_at = parts[2].removesuffix(".json.gz")
        if month not in newest or fetched_at > newest[month][0]:
            newest[month] = (fetched_at, path)
    if not newest:
        raise FileNotFoundError("No shared or legacy physical-market snapshots found")

    selected_rows: list[dict[str, Any]] = []
    for month, (snapshot_time, path) in sorted(newest.items()):
        with gzip.open(path, "rt", encoding="utf-8") as handle:
            archive = json.load(handle)
        raw_response = str(archive["response_utf8"]).encode("utf-8")
        outer = json.loads(raw_response.decode("utf-8-sig"))
        all_rows = json.loads(outer["d"])
        selected = [row for row in all_rows if config.row_filter(row)]
        validate_selected(selected, config)
        fetched_at = str(archive.get("fetched_at_utc") or snapshot_time)
        source_url = str(archive.get("source_url") or API_URL)
        for row in selected:
            normalized = {field: row.get(field) for field in SOURCE_COLUMNS}
            normalized.update(fetched_at_utc=fetched_at, source_url=source_url)
            selected_rows.append(normalized)
    validate_selected(selected_rows, config)
    write_csv_atomic(csv_path, selected_rows)
    print(f"Rebuilt {csv_path} from {len(newest)} monthly snapshots; rows: {len(selected_rows)}")


def collect(
    config: PhysicalCollectorConfig,
    timeout: int = 120,
    retries: int = 3,
    refresh_months: int = 2,
    start_override: str | None = None,
    end_override: str | None = None,
) -> None:
    raw_dir = config.project_dir / "data" / "raw" / "physical"
    csv_path = raw_dir / config.output_filename
    existing = read_existing(csv_path)
    today_j = gregorian_to_jalali(*datetime.now().date().timetuple()[:3])
    end = tuple(map(int, end_override.split("/"))) if end_override else today_j[:2]
    if start_override:
        start = tuple(map(int, start_override.split("/")))
    elif existing:
        dates = [str(row["date"]).replace("-", "/").split("/") for row in existing]
        newest = max((int(parts[0]), int(parts[1])) for parts in dates if len(parts) >= 2)
        absolute = newest[0] * 12 + newest[1] - 1 - refresh_months
        start = max(FIRST_JALALI_MONTH, (absolute // 12, absolute % 12 + 1))
    else:
        start = FIRST_JALALI_MONTH
    if start > end:
        raise ValueError(f"start month {start} is after end month {end}")

    fetched_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    fetched: list[dict[str, Any]] = []
    refreshed_months = set(iter_months(start, end))
    print(f"Existing {config.target_label} rows: {len(existing)}")
    print(f"Query months: {start[0]:04d}/{start[1]:02d} through {end[0]:04d}/{end[1]:02d}")
    for year, month in iter_months(start, end):
        last_day = today_j[2] if (year, month) == today_j[:2] else month_end(year, month)
        from_date = f"{year:04d}/{month:02d}/01"
        to_date = f"{year:04d}/{month:02d}/{last_day:02d}"
        payload = {
            "Language": 8,
            "fari": False,
            "GregorianFromDate": from_date,
            "GregorianToDate": to_date,
            "MainCat": 0,
            "Cat": 0,
            "SubCat": 0,
            "Producer": 0,
        }
        raw_response, all_rows = fetch_rows(payload, timeout, retries)
        selected = [row for row in all_rows if config.row_filter(row)]
        validate_selected(selected, config)
        snapshot_path = archive_market_response(
            raw_response, payload, fetched_at, year, month, config.shared_snapshot_dir
        )
        with gzip.open(snapshot_path, "rt", encoding="utf-8") as handle:
            archived_fetch_time = str(json.load(handle)["fetched_at_utc"])
        for row in selected:
            normalized = {field: row.get(field) for field in SOURCE_COLUMNS}
            normalized.update(fetched_at_utc=archived_fetch_time, source_url=API_URL)
            fetched.append(normalized)
        print(
            f"  {from_date}..{to_date}: {len(all_rows)} market rows, {len(selected)} selected rows"
        )

    def row_month(row: dict[str, Any]) -> tuple[int, int] | None:
        parts = str(row.get("date", "")).replace("-", "/").split("/")
        try:
            return int(parts[0]), int(parts[1])
        except (ValueError, IndexError):
            return None

    retained = [row for row in existing if row_month(row) not in refreshed_months]
    merged = retained + fetched
    validate_selected(merged, config)
    write_csv_atomic(csv_path, merged)
    print(f"Saved rows: {len(merged)}; fetched this run: {len(fetched)}")
    print(f"Goods retained: {sorted({str(row['GoodsName']) for row in merged})}")
    print(f"Output: {csv_path}")
