"""Network-free tests for the global copper-market collector primitives."""

from __future__ import annotations

import unittest

from commodity.copper.src.copper.collectors.global_market import FRED_SERIES, NBS_SERIES


class GlobalMarketRegistryTests(unittest.TestCase):
    def test_existing_lme_is_not_recollected(self) -> None:
        self.assertNotIn("LME", FRED_SERIES)

    def test_required_public_series_are_registered(self) -> None:
        self.assertTrue({"DTWEXBGS", "EFFR", "DGS10", "DFII10", "DEXCHUS"} <= FRED_SERIES.keys())
        self.assertTrue({"WPU10230101", "WPU10230102"} <= FRED_SERIES.keys())
        self.assertEqual(set(NBS_SERIES), {"A02091J01", "A02091J02", "A02091J03", "A02091J04"})


if __name__ == "__main__":
    unittest.main()
