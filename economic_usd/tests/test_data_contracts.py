import csv
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class DataContracts(unittest.TestCase):
    def rows(self, name):
        with (ROOT / "data" / "processed" / name).open(encoding="utf-8-sig", newline="") as f:
            return list(csv.DictReader(f))

    def test_liquidity_identity_and_unique_months(self):
        rows = self.rows("iran_liquidity.csv")
        self.assertEqual(len(rows), len({r["solar_hijri_period"] for r in rows}))
        for r in rows:
            self.assertAlmostEqual(float(r["iran_liquidity_thousand_billion_irr"]), float(r["money_thousand_billion_irr"]) + float(r["quasi_money_thousand_billion_irr"]), places=1)

    def test_cpi_is_unique_monthly_index(self):
        rows = self.rows("iran_urban_headline_cpi.csv")
        self.assertEqual(len(rows), len({r["solar_hijri_period"] for r in rows}))
        self.assertTrue(all(float(r["iran_urban_headline_cpi"]) > 0 for r in rows))

    def test_usd_unit_and_unique_dates(self):
        rows = self.rows("usd_free_market.csv")
        self.assertEqual(len(rows), len({r["date_jalali"] for r in rows}))
        self.assertTrue(all(r["unit"] == "IRR_per_USD" for r in rows))

    def test_us_cpi_series(self):
        rows = self.rows("us_cpi_urban_all_items.csv")
        self.assertTrue(all(r["series_id"] == "CPIAUCNS" for r in rows))
        self.assertEqual(len(rows), len({r["date"] for r in rows}))


if __name__ == "__main__":
    unittest.main()

