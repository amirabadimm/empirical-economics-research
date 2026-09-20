from __future__ import annotations

import csv
import hashlib
import json
import os
import tempfile
import time
from datetime import date
from pathlib import Path
from typing import Any

import jdatetime
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

ROOT = Path(__file__).resolve().parents[2]
UNDERLYING_CODE = "17914401175772326"
UNDERLYING_SYMBOL = "اهرم"


class RawJson(dict):
    def __init__(self, value: dict, payload: bytes):
        super().__init__(value)
        self.payload = payload


def session() -> requests.Session:
    result = requests.Session()
    retry = Retry(total=4, connect=4, read=4, backoff_factor=1.2,
                  status_forcelist=(429, 500, 502, 503, 504),
                  allowed_methods=("GET",), respect_retry_after_header=True)
    result.mount("https://", HTTPAdapter(max_retries=retry))
    result.headers.update({"User-Agent": "ahrom-options-research/1.0", "Accept": "application/json"})
    return result


def fetch_json(client: requests.Session, url: str, *, params: dict | None = None,
               cookies: dict | None = None, delay: float = 0.25) -> dict:
    try:
        response = client.get(url, params=params, cookies=cookies, timeout=(10, 30))
        response.raise_for_status()
        result = response.json()
        if not isinstance(result, dict):
            raise ValueError("Expected a JSON object")
        return RawJson(result, response.content)
    finally:
        time.sleep(delay)


def archive_json(directory: Path, body: dict) -> Path:
    payload = getattr(body, "payload", None)
    if payload is None:
        payload = json.dumps(body, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    digest = hashlib.sha256(payload).hexdigest()
    destination = directory / f"{digest}.json"
    if destination.exists():
        if destination.read_bytes() != payload:
            raise ValueError(f"Archive integrity mismatch: {destination}")
        return destination
    directory.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".capture-", dir=directory)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        replace_with_retry(name, destination)
    finally:
        if os.path.exists(name):
            os.unlink(name)
    return destination


def read_archive(path: Path) -> dict:
    payload = path.read_bytes()
    if hashlib.sha256(payload).hexdigest() != path.stem:
        raise ValueError(f"Archive hash mismatch: {path}")
    result = json.loads(payload)
    if not isinstance(result, dict):
        raise ValueError(f"Archive is not a JSON object: {path}")
    return result


def replace_with_retry(source: str, destination: Path) -> None:
    for attempt in range(5):
        try:
            os.replace(source, destination)
            return
        except PermissionError:
            if attempt == 4:
                raise
            time.sleep(0.2 * (attempt + 1))


def atomic_bytes(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".build-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as output:
            output.write(payload)
            output.flush()
            os.fsync(output.fileno())
        replace_with_retry(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def atomic_csv(path: Path, rows: list[dict[str, Any]], columns: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(prefix=".build-", dir=path.parent, text=True)
    try:
        with os.fdopen(fd, "w", encoding="utf-8-sig", newline="") as output:
            writer = csv.DictWriter(output, fieldnames=columns, extrasaction="ignore")
            writer.writeheader()
            writer.writerows(rows)
            output.flush()
            os.fsync(output.fileno())
        replace_with_retry(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def jalali_to_gregorian(value: str) -> str:
    year, month, day = (int(part) for part in value.split("/"))
    return jdatetime.date(year, month, day).togregorian().isoformat()


def today() -> str:
    return date.today().isoformat()
