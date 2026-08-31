"""Network-free contracts for the steel rebar collection pipeline."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys

import pandas as pd


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.rebar.src.rebar.collectors.physical import is_rebar
from commodity.rebar.src.rebar.collectors.certificate import CONFIG as CERTIFICATE_CONFIG
from commodity.rebar.src.rebar.processing.rebar_scope import (
    A3_12_PRODUCT,
    A3_18_PRODUCT,
    canonical_straight_rebar_label,
    is_a3_12_straight_rebar,
    is_a3_18_straight_rebar,
)
from commodity.rebar.src.rebar.processing.build_a3_12_cash_daily import build_daily
from commodity.rebar.src.rebar.processing.build_a3_18_exact_bubble import build_exact_bubble
from commodity.rebar.src.rebar.processing.build_a3_12_exact_bubble import (
    build as build_a3_12_exact_bubble,
)
from shared.ime_data.ime_physical_collector import normalize_fa


class RebarScopeTests(unittest.TestCase):
    def test_certificate_identity_is_continuous_across_code_change(self) -> None:
        self.assertEqual(CERTIFICATE_CONFIG.commodity_id, "29")
        self.assertEqual(CERTIFICATE_CONFIG.codes, {"CD1RBR0001", "SteelRebar"})

    def test_rebar_scope_accepts_normalized_rebar_labels(self) -> None:
        self.assertTrue(is_rebar({"GoodsName": "\u0645\u06cc\u0644\u06af\u0631\u062f A3"}))
        self.assertTrue(is_rebar({"GoodsName": "  \u0645\u064a\u0644\u06af\u0631\u062f   16 "}))
        self.assertFalse(is_rebar({"GoodsName": "\u0634\u0645\u0634 \u0641\u0648\u0644\u0627\u062f\u06cc"}))
        self.assertFalse(is_rebar({"GoodsName": ""}))

    def test_scope_does_not_change_source_values(self) -> None:
        source_label = "\u0645\u064a\u0644\u06af\u0631\u062f 12"
        self.assertEqual(normalize_fa(source_label), "\u0645\u06cc\u0644\u06af\u0631\u062f 12")

    def test_a3_12_scope_normalizes_label_order_and_excludes_mixed_products(self) -> None:
        self.assertEqual(canonical_straight_rebar_label("\u0645\u06cc\u0644\u06af\u0631\u062f 12-A3"), A3_12_PRODUCT)
        self.assertTrue(is_a3_12_straight_rebar("\u0645\u06cc\u0644\u06af\u0631\u062f A3-12"))
        self.assertFalse(is_a3_12_straight_rebar("\u0633\u0628\u062f \u0645\u06cc\u0644\u06af\u0631\u062f 12-A3"))
        self.assertFalse(is_a3_12_straight_rebar("\u0645\u06cc\u0644\u06af\u0631\u062f 12 \u0648 14-A3"))

    def test_daily_vwap_filters_to_a3_12_before_aggregation(self) -> None:
        raw = pd.DataFrame([
            {
                "GoodsName": "\u0645\u06cc\u0644\u06af\u0631\u062f 12-A3", "Symbol": "A3-12", "ProducerName": "P1",
                "ContractType": "\u0646\u0642\u062f\u06cc", "date": "1405/01/01", "Price": "100",
                "ArzeBasePrice": "80", "Quantity": "10",
            },
            {
                "GoodsName": "\u0645\u06cc\u0644\u06af\u0631\u062f A3-12", "Symbol": "A3-12", "ProducerName": "P2",
                "ContractType": "\u0646\u0642\u062f\u06cc (\u0645\u0686\u06cc\u0646\u06af)", "date": "1405/01/01", "Price": "200",
                "ArzeBasePrice": "160", "Quantity": "10",
            },
            {
                "GoodsName": "\u0645\u06cc\u0644\u06af\u0631\u062f 10-A3", "Symbol": "A3-10", "ProducerName": "P3",
                "ContractType": "\u0646\u0642\u062f\u06cc", "date": "1405/01/01", "Price": "999999",
                "ArzeBasePrice": "999999", "Quantity": "1000",
            },
        ])

        daily = build_daily(raw)

        self.assertEqual(len(daily), 1)
        self.assertEqual(float(daily.loc[0, "cash_trade_price_vwap"]), 150.0)
        self.assertEqual(float(daily.loc[0, "offer_base_price_vwap"]), 120.0)
        self.assertEqual(float(daily.loc[0, "traded_quantity"]), 20.0)
        self.assertNotIn("A3-10", daily.loc[0, "symbols"])

    def test_a3_18_scope_is_strict(self) -> None:
        self.assertEqual(canonical_straight_rebar_label("میلگرد 18-A3"), A3_18_PRODUCT)
        self.assertTrue(is_a3_18_straight_rebar("میلگرد A3-18"))
        self.assertFalse(is_a3_18_straight_rebar("سبد میلگرد 18-A3"))
        self.assertFalse(is_a3_18_straight_rebar("میلگرد 16-A3"))

    def test_exact_bubble_uses_only_same_day_cash_a3_18(self) -> None:
        physical = pd.DataFrame([
            {
                "GoodsName": "میلگرد 18-A3", "Symbol": "R18", "ProducerName": "P1",
                "ContractType": "نقدی", "Currency": "ریال", "Unit": "تن",
                "date": "1405/01/11", "Price": "500", "Quantity": "10",
            },
            {
                "GoodsName": "میلگرد A3-18", "Symbol": "R18B", "ProducerName": "P2",
                "ContractType": "نقدی (مچینگ)", "Currency": "ریال", "Unit": "تن",
                "date": "1405/01/11", "Price": "700", "Quantity": "10",
            },
            {
                "GoodsName": "میلگرد 18-A3", "Symbol": "FORWARD", "ProducerName": "P3",
                "ContractType": "سلف", "Currency": "ریال", "Unit": "تن",
                "date": "1405/01/11", "Price": "9999", "Quantity": "1000",
            },
            {
                "GoodsName": "میلگرد 12-A3", "Symbol": "R12", "ProducerName": "P4",
                "ContractType": "نقدی", "Currency": "ریال", "Unit": "تن",
                "date": "1405/01/11", "Price": "9999", "Quantity": "1000",
            },
        ])
        certificate = pd.DataFrame([{
            "CommodityID": "29", "ContractCode": "SteelRebar",
            "DT": "2026-03-31T00:00:00", "PersianDate": "1405/01/11",
            "TradesVolume": "20", "TradesValue": "13000", "TodaySettlementPrice": "650",
        }])

        bubble = build_exact_bubble(physical, certificate)

        self.assertEqual(len(bubble), 1)
        self.assertEqual(float(bubble.loc[0, "physical_price_irr_per_kg"]), 600.0)
        self.assertAlmostEqual(
            float(bubble.loc[0, "certificate_vs_physical_bubble_pct"]),
            100 * (650 / 600 - 1),
        )
        self.assertEqual(bubble.loc[0, "alignment_method"], "exact_date_observed_cash_a3_18")

    def test_a3_12_bubble_is_labeled_as_cross_diameter_diagnostic(self) -> None:
        physical = pd.DataFrame([{
            "GoodsName": "میلگرد 12-A3", "Symbol": "R12", "ProducerName": "P1",
            "ContractType": "نقدی", "Currency": "ریال", "Unit": "تن",
            "date": "1405/01/11", "Price": "500", "Quantity": "10",
        }])
        certificate = pd.DataFrame([{
            "CommodityID": "29", "ContractCode": "SteelRebar",
            "DT": "2026-03-31T00:00:00", "PersianDate": "1405/01/11",
            "TradesVolume": "20", "TradesValue": "13000", "TodaySettlementPrice": "650",
        }])

        bubble = build_a3_12_exact_bubble(physical, certificate)

        self.assertEqual(bubble.loc[0, "physical_product_scope"], A3_12_PRODUCT)
        self.assertEqual(
            bubble.loc[0, "comparability_status"],
            "intentional_cross_diameter_diagnostic_not_underlying_match",
        )
        self.assertEqual(
            bubble.loc[0, "alignment_method"],
            "exact_date_observed_cash_a3_12_cross_diameter",
        )

if __name__ == "__main__":
    unittest.main()
