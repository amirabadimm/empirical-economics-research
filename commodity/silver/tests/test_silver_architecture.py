"""Network-free contracts for the silver architecture."""
import unittest
import pandas as pd

from commodity.silver.src.silver.collectors.certificate import CONFIG
from commodity.silver.src.silver.collectors.physical import is_silver_related
from commodity.silver.src.silver.processing.build_certificate_bubble import build as build_bubble
from commodity.silver.src.silver.processing.build_physical_benchmark import build as build_physical, is_9999_silver_bar

class SilverArchitectureTests(unittest.TestCase):
    def test_certificate_identity(self):
        self.assertEqual(CONFIG.commodity_id, "21")
        self.assertEqual(CONFIG.codes, {"CD1SIB0001", "SilverBar"})

    def test_broad_and_strict_scopes(self):
        self.assertTrue(is_silver_related({"GoodsName": "ساچمه نقره"}))
        self.assertFalse(is_silver_related({"GoodsName": "شمش طلا 995"}))
        self.assertTrue(is_9999_silver_bar("شمش نقره 999.9"))
        self.assertFalse(is_9999_silver_bar("شمش نقره 925"))

    def test_vwap_and_explicit_gram_to_kg_conversion(self):
        raw = pd.DataFrame([
            {"GoodsName": "شمش نقره 999.9", "Symbol": "S1", "ProducerName": "P1",
             "ContractType": "نقدی", "Currency": "ریال", "Unit": "کیلوگرم",
             "date": "1405/01/11", "Price": 2_000_000, "Quantity": 10},
            {"GoodsName": "شمش نقره 999.9", "Symbol": "S2", "ProducerName": "P2",
             "ContractType": "نقدی (مچینگ)", "Currency": "ریال", "Unit": "کیلوگرم",
             "date": "1405/01/11", "Price": 4_000_000, "Quantity": 10},
        ])
        physical = build_physical(raw)
        self.assertEqual(float(physical.loc[0, "physical_price_irr_per_kg"]), 3_000_000)
        certificate = pd.DataFrame([{"PersianDate": "1405/01/11",
            "DT": "2026-03-31T00:00:00", "TradesVolume": 25,
            "TodaySettlementPrice": 3_300}])
        bubble = build_bubble(certificate, physical)
        self.assertEqual(float(bubble.loc[0, "certificate_price_irr_per_kg"]), 3_300_000)
        self.assertAlmostEqual(float(bubble.loc[0, "premium_discount_pct"]), 10.0)

    def test_exact_date_is_required(self):
        physical = pd.DataFrame([{"date_jalali": "1405/01/12",
            "physical_price_irr_per_kg": 3_000_000, "physical_quantity_kg": 10,
            "physical_product_scope": "scope", "price_method": "method"}])
        certificate = pd.DataFrame([{"PersianDate": "1405/01/11",
            "DT": "2026-03-31T00:00:00", "TradesVolume": 25,
            "TodaySettlementPrice": 3_300}])
        with self.assertRaisesRegex(ValueError, "No exact-date"):
            build_bubble(certificate, physical)

if __name__ == "__main__":
    unittest.main()
