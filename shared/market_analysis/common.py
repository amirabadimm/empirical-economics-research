"""Validated scalar, CSV, and as-of helpers for cross-commodity analysis."""

from __future__ import annotations

import bisect
import csv
from datetime import date
from decimal import Decimal, InvalidOperation
from pathlib import Path


def number(value: object, field: str, row_date: str) -> Decimal:
    try:
        return Decimal(str(value).replace(",", "").strip())
    except InvalidOperation as exc:
        raise ValueError(f"Invalid {field} on {row_date}: {value!r}") from exc


def display(value: Decimal | None) -> str:
    if value is None:
        return ""
    if value == value.to_integral_value():
        return str(int(value))
    return format(value.normalize(), "f")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def write_atomic(path: Path, columns: list[str], rows: list[dict[str, str]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_suffix(path.suffix + ".tmp")
    with temporary.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    temporary.replace(path)


def parse_mixed_gregorian(value: str) -> date:
    first, second, third = map(int, value.strip().replace("-", "/").split("/"))
    return date(first, second, third) if first >= 1900 else date(third, first, second)


def asof_value(
    target: date, dates: list[date], values: dict[date, Decimal], label: str
) -> tuple[date, Decimal]:
    index = bisect.bisect_right(dates, target) - 1
    if index < 0:
        raise ValueError(f"No prior {label} observation for {target}")
    source_date = dates[index]
    return source_date, values[source_date]
