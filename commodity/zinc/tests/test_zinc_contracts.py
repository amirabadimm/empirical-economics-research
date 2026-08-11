"""Network-free regression tests for the Zinc raw-data contracts."""

from __future__ import annotations

import csv
import gzip
import json
import tempfile
import unittest
from pathlib import Path
import sys


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
PROJECT_DIR = Path(__file__).resolve().parents[1]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.zinc.src.zinc.collectors.certificate import CONFIG as CERTIFICATE_CONFIG
from commodity.zinc.src.zinc.collectors.lme import (
    OUTPUT_COLUMNS as LME_COLUMNS,
    build_url as build_lme_url,
    parse_page as parse_lme_page,
    read_existing as read_existing_lme,
    write_csv_atomic as write_lme_csv_atomic,
)
from commodity.zinc.src.zinc.collectors.physical import is_zinc_related
from shared.ime_data.certificate_collector import (
    RAW_COLUMNS as CERTIFICATE_COLUMNS,
    validate_record,
)
from shared.ime_data.ime_physical_collector import (
    API_URL as PHYSICAL_API_URL,
    RAW_COLUMNS as PHYSICAL_COLUMNS,
    SOURCE_COLUMNS,
    PhysicalCollectorConfig,
    rebuild_from_snapshots,
)


def _physical_config(project_dir: Path) -> PhysicalCollectorConfig:
    return PhysicalCollectorConfig(
        project_dir=project_dir,
        output_filename="zinc_physical_raw.csv",
        snapshot_prefix="physical",
        target_label="zinc-related",
        row_filter=is_zinc_related,
    )


def _read_csv(path: Path) -> tuple[list[str], list[dict[str, str]]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        return list(reader.fieldnames or []), list(reader)


def _archive(path: Path, rows: list[dict[str, object]]) -> None:
    outer_response = json.dumps({"d": json.dumps(rows, ensure_ascii=False)}, ensure_ascii=False)
    payload = {
        "request": {},
        "fetched_at_utc": "2026-08-10T00:00:00+00:00",
        "source_url": PHYSICAL_API_URL,
        "response_utf8": outer_response,
    }
    with gzip.open(path, "wt", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False)


class ZincScopeTests(unittest.TestCase):
    def test_scope_keeps_ingot_and_soil_but_rejects_other_metals(self) -> None:
        self.assertTrue(is_zinc_related({"GoodsName": "شمش روی 99.98"}))
        self.assertTrue(is_zinc_related({"GoodsName": "خاک روي"}))
        self.assertFalse(is_zinc_related({"GoodsName": "مس کاتد"}))
        self.assertFalse(is_zinc_related({"GoodsName": None}))

    def test_certificate_identity_is_a_continuous_two_code_series(self) -> None:
        self.assertEqual(CERTIFICATE_CONFIG.commodity_id, "30")
        self.assertEqual(CERTIFICATE_CONFIG.codes, {"CD1ZNI0001", "ZincIngot"})


class ZincCanonicalDataTests(unittest.TestCase):
    def test_certificate_schema_identity_values_and_unique_dates(self) -> None:
        path = PROJECT_DIR / "data" / "raw" / "certificate" / "zinc_certificate_raw.csv"
        if not path.exists():
            self.skipTest("local canonical certificate CSV is not available")
        columns, rows = _read_csv(path)
        self.assertEqual(columns, CERTIFICATE_COLUMNS)
        dates: list[str] = []
        for row in rows:
            validate_record(row, CERTIFICATE_CONFIG)
            dates.append(row["DT"][:10])
        self.assertEqual(len(dates), len(set(dates)))
        self.assertEqual(dates, sorted(dates))

    def test_physical_schema_scope_values_and_commercial_keys(self) -> None:
        path = PROJECT_DIR / "data" / "raw" / "physical" / "zinc_physical_raw.csv"
        if not path.exists():
            self.skipTest("local canonical physical CSV is not available")
        columns, rows = _read_csv(path)
        self.assertEqual(columns, PHYSICAL_COLUMNS)
        fingerprints: set[tuple[str, ...]] = set()
        commercial_keys: set[tuple[str, str, str, str]] = set()
        for row in rows:
            self.assertTrue(is_zinc_related(row))
            self.assertGreaterEqual(float(row["Quantity"] or 0), 0)
            self.assertGreaterEqual(float(row["Price"] or 0), 0)
            self.assertTrue(row["date"] and row["Symbol"] and row["ProducerName"])
            fingerprint = tuple(row[column] for column in PHYSICAL_COLUMNS)
            self.assertNotIn(fingerprint, fingerprints)
            fingerprints.add(fingerprint)
            key = (row["date"], row["Symbol"], row["arzehPk"], row["ContractType"])
            self.assertNotIn(key, commercial_keys)
            commercial_keys.add(key)

    def test_newest_snapshot_for_each_month_is_parseable(self) -> None:
        directory = PROJECT_DIR / "data" / "raw" / "physical" / "api_snapshots"
        if not directory.exists():
            self.skipTest("local physical snapshots are not available")
        newest: dict[str, Path] = {}
        for path in sorted(directory.glob("physical_*.json.gz")):
            newest[path.name.split("_")[1]] = path
        self.assertTrue(newest)
        for month, path in newest.items():
            with self.subTest(month=month, snapshot=path.name):
                with gzip.open(path, "rt", encoding="utf-8") as handle:
                    archive = json.load(handle)
                outer = json.loads(archive["response_utf8"])
                rows = json.loads(outer["d"])
                self.assertIsInstance(rows, list)


class ZincSnapshotRebuildTests(unittest.TestCase):
    def test_rebuild_uses_newest_snapshot_without_mutating_archives(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            project_dir = Path(temporary)
            snapshots = project_dir / "data" / "raw" / "physical" / "api_snapshots"
            snapshots.mkdir(parents=True)
            old_path = snapshots / "physical_1403-11_20260801T000000Z.json.gz"
            old_path.write_bytes(b"immutable-corrupt-snapshot")
            old_bytes = old_path.read_bytes()

            row = {column: 0 for column in SOURCE_COLUMNS}
            row.update(
                GoodsName="شمش روی 99.98",
                Symbol="TEST-ZINC-00",
                ProducerName="تولیدکننده آزمون",
                ContractType="نقدی",
                date="1403/11/01",
                arzehPk="1",
            )
            newest_path = snapshots / "physical_1403-11_20260810T000000Z.json.gz"
            _archive(newest_path, [row])

            rebuild_from_snapshots(_physical_config(project_dir))

            output = project_dir / "data" / "raw" / "physical" / "zinc_physical_raw.csv"
            columns, rebuilt = _read_csv(output)
            self.assertEqual(columns, PHYSICAL_COLUMNS)
            self.assertEqual(len(rebuilt), 1)
            self.assertEqual(rebuilt[0]["Symbol"], "TEST-ZINC-00")
            self.assertEqual(old_path.read_bytes(), old_bytes)
            self.assertTrue(newest_path.exists())


class ZincLmeCollectorTests(unittest.TestCase):
    def test_url_uses_zinc_cash_field(self) -> None:
        self.assertEqual(
            build_lme_url(2026),
            "https://www.westmetall.com/en/markdaten.php?"
            "action=table&field=LME_Zn_cash&year=2026",
        )

    def test_parser_ignores_repeated_headers_and_preserves_source_values(self) -> None:
        html = b"""
        <table>
          <tr><th>Date</th><th>LME Zinc Cash-Settlement</th><th>3-month</th><th>Stock</th></tr>
          <tr><td>2. January 2026</td><td>3,125.50</td><td>3,100.00</td><td>91,250</td></tr>
          <tr><th>Date</th><th>Cash</th><th>3-month</th><th>Stock</th></tr>
          <tr><td>5. January 2026</td><td>-</td><td>3,090.00</td><td>90,900</td></tr>
        </table>
        """
        rows = parse_lme_page(html, 2026, "2026-08-10T00:00:00+00:00", "source")
        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["date"], "2026-01-02")
        self.assertEqual(rows[0]["cash_settlement"], "3,125.50")
        self.assertEqual(rows[1]["cash_settlement"], "-")

    def test_atomic_writer_produces_sorted_unique_canonical_csv(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "zinc_lme_raw.csv"
            base = {column: "" for column in LME_COLUMNS}
            records = {
                "2026-01-05": base | {"date": "2026-01-05", "cash_settlement": "3,100"},
                "2026-01-02": base | {"date": "2026-01-02", "cash_settlement": "3,125"},
            }
            write_lme_csv_atomic(path, records)
            loaded = read_existing_lme(path)
            self.assertEqual(list(loaded), ["2026-01-02", "2026-01-05"])
            self.assertFalse(path.with_suffix(".csv.tmp").exists())

    def test_local_canonical_lme_schema_dates_and_source_identity(self) -> None:
        path = PROJECT_DIR / "data" / "raw" / "lme" / "zinc_lme_raw.csv"
        if not path.exists():
            self.skipTest("local canonical LME Zinc CSV is not available")
        columns, rows = _read_csv(path)
        self.assertEqual(columns, LME_COLUMNS)
        dates = [row["date"] for row in rows]
        self.assertEqual(dates, sorted(dates))
        self.assertEqual(len(dates), len(set(dates)))
        self.assertTrue(all(row["source_year"] == row["date"][:4] for row in rows))
        self.assertTrue(all("field=LME_Zn_cash" in row["source_url"] for row in rows))


if __name__ == "__main__":
    unittest.main()
