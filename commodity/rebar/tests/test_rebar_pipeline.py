"""Network-free contracts for the steel rebar collection pipeline."""

from __future__ import annotations

import unittest
from pathlib import Path
import sys


WORKSPACE_ROOT = Path(__file__).resolve().parents[3]
if str(WORKSPACE_ROOT) not in sys.path:
    sys.path.insert(0, str(WORKSPACE_ROOT))

from commodity.rebar.src.rebar.collectors.physical import is_rebar
from commodity.rebar.src.rebar.processing.rebar_scope import (
    A3_12_PRODUCT,
    canonical_straight_rebar_label,
    is_a3_12_straight_rebar,
)
from shared.ime_data.ime_physical_collector import normalize_fa


class RebarScopeTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
