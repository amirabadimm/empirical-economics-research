"""Network-free contracts for the shared USD/IRR collector."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from shared.market_data.fx import CSV_PATH, archive_snapshot, canonical_dates, parse_tgju


class SharedFxTests(unittest.TestCase):
    def test_canonical_path_is_outside_every_commodity_project(self) -> None:
        self.assertEqual(CSV_PATH.as_posix().split("/")[-5:], [
            "shared", "data", "raw", "fx", "usd_to_rial.csv"
        ])

    def test_jalali_and_gregorian_dates_reconcile(self) -> None:
        self.assertEqual(canonical_dates("1405/05/31"), ("1405/05/31", "2026/8/22"))

    def test_tgju_parser_uses_closing_price(self) -> None:
        html = """
        <table><tbody id="table-list"><tr>
        <td>1,000</td><td>900</td><td>1,100</td><td>1,050</td>
        <td>50</td><td>5%</td><td>2026/08/22</td><td>1405/05/31</td>
        </tr></tbody></table>
        """.encode()
        rows = parse_tgju(html)
        self.assertEqual(rows[0]["price_irr"], "1,050")
        self.assertEqual(rows[0]["price_method"], "close")

    def test_snapshot_collision_never_overwrites_source_material(self) -> None:
        with TemporaryDirectory() as directory:
            snapshot_dir = Path(directory)
            first = archive_snapshot(b"first", snapshot_dir, "20260829T000000Z")
            second = archive_snapshot(b"second", snapshot_dir, "20260829T000000Z")
            self.assertNotEqual(first, second)
            self.assertEqual(first.read_bytes(), b"first")
            self.assertEqual(second.read_bytes(), b"second")


if __name__ == "__main__":
    unittest.main()
