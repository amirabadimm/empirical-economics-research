"""Network-free tests for the UN Comtrade copper collector."""

from __future__ import annotations

import unittest

from commodity.copper.src.copper.collectors.comtrade import month_range


class MonthRangeTests(unittest.TestCase):
    def test_crosses_year_boundary(self) -> None:
        self.assertEqual(month_range("202311", "202402"), ["202311", "202312", "202401", "202402"])

    def test_single_month(self) -> None:
        self.assertEqual(month_range("202501", "202501"), ["202501"])


if __name__ == "__main__":
    unittest.main()
