"""Network-free tests for CME stock parsing helpers."""

from __future__ import annotations

import unittest

from commodity.copper.src.copper.collectors.cme import numeric


class NumericTests(unittest.TestCase):
    def test_numeric_and_missing_cells(self) -> None:
        self.assertEqual(numeric("1,234"), 1234.0)
        self.assertIsNone(numeric("--"))


if __name__ == "__main__":
    unittest.main()
