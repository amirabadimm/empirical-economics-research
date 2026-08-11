"""Fast, network-free regression tests for shared market contracts."""

from __future__ import annotations

import unittest
from datetime import date
from pathlib import Path
import sys


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.copper.src.copper.collectors.physical import is_approved_copper_cathode
from shared.ime_data.certificate_collector import chunks
from shared.ime_data.ime_physical_collector import (
    gregorian_to_jalali,
    jalali_to_gregorian,
    month_end,
    normalize_fa,
)


class CalendarTests(unittest.TestCase):
    def test_round_trip_known_dates(self) -> None:
        for gregorian in ((2008, 8, 24), (2025, 10, 20), (2026, 8, 2)):
            jalali = gregorian_to_jalali(*gregorian)
            self.assertEqual(jalali_to_gregorian(*jalali), gregorian)

    def test_jalali_month_lengths(self) -> None:
        self.assertEqual(month_end(1405, 1), 31)
        self.assertEqual(month_end(1405, 7), 30)
        self.assertIn(month_end(1405, 12), (29, 30))

    def test_certificate_chunks_are_contiguous(self) -> None:
        result = list(chunks(date(2025, 10, 20), date(2026, 8, 2)))
        self.assertEqual(result[0][0], date(2025, 10, 20))
        self.assertEqual(result[-1][1], date(2026, 8, 2))
        for previous, current in zip(result, result[1:]):
            self.assertEqual((current[0] - previous[1]).days, 1)


class ScopeTests(unittest.TestCase):
    def test_persian_normalization(self) -> None:
        self.assertEqual(normalize_fa("  كاتد ي  "), "کاتد ی")

    def test_copper_scope_accepts_only_approved_rows(self) -> None:
        approved = {
            "GoodsName": "مس کاتد",
            "Symbol": "NCI-OACCAA-00",
            "ContractType": "نقدی (مچینگ)",
        }
        self.assertTrue(is_approved_copper_cathode(approved))
        self.assertFalse(is_approved_copper_cathode(approved | {"ContractType": "سلف"}))
        self.assertFalse(is_approved_copper_cathode(approved | {"Symbol": "OTHER"}))


if __name__ == "__main__":
    unittest.main()
