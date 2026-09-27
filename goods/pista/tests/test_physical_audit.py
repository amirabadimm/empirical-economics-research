"""Evidence and preservation checks for the weekly price audit."""

import sys
import unittest
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from analysis.audit_physical import DATE_COLUMN, PRODUCTS, audit  # noqa: E402


def weekly_frame(dates, khandan, dahan_bast=None):
    dahan_bast = dahan_bast or khandan
    frame = pd.DataFrame({DATE_COLUMN: dates})
    for product, values in zip(PRODUCTS, (khandan, dahan_bast)):
        frame[f"{product} Min Price"] = [pair[0] for pair in values]
        frame[f"{product} Max Price"] = [pair[1] for pair in values]
        frame[f"{product} Average Price"] = [
            (pair[0] + pair[1]) / 2 if pair[0] is not None and pair[1] is not None else None
            for pair in values
        ]
    return frame


class PhysicalAuditTests(unittest.TestCase):
    def test_recomputes_only_deterministic_average_error(self):
        frame = weekly_frame(
            ["1404/01/07", "1404/01/14", "1404/01/21"],
            [(100, 100), (100, 100), (100, 100)],
        )
        frame.at[1, "Khandan Average Price"] = 999
        cleaned, findings = audit(frame)
        self.assertEqual(cleaned.at[1, "Khandan Average Price"], 100)
        self.assertEqual(cleaned.at[1, "Khandan Min Price"], 100)
        self.assertEqual(findings.loc[findings["action"].eq("correct"), "jalali_date"].tolist(), ["1404/01/14"])

    def test_ambiguous_range_and_isolated_drop_are_unchanged(self):
        frame = weekly_frame(
            ["1404/01/07", "1404/01/14", "1404/01/21"],
            [(100, 110), (10, 110), (100, 110)],
        )
        cleaned, findings = audit(frame)
        self.assertEqual(cleaned.at[1, "Khandan Min Price"], 10)
        self.assertEqual(findings.loc[findings["product"].eq("Khandan"), "action"].iloc[0], "manual_review")

    def test_missing_derived_average_is_recomputed(self):
        frame = weekly_frame(
            ["1404/01/07", "1404/01/14", "1404/01/21"],
            [(100, 100), (100, 100), (100, 100)],
        )
        frame.at[1, "Khandan Average Price"] = None
        cleaned, findings = audit(frame)
        self.assertEqual(cleaned.at[1, "Khandan Average Price"], 100)
        self.assertEqual(findings.loc[findings["product"].eq("Khandan"), "action"].iloc[0], "correct")

    def test_persistent_jump_is_not_changed(self):
        frame = weekly_frame(
            ["1404/01/07", "1404/01/14", "1404/01/21"],
            [(100, 100), (150, 150), (150, 150)],
        )
        cleaned, findings = audit(frame)
        self.assertEqual(cleaned.at[1, "Khandan Average Price"], 150)
        self.assertEqual(findings.loc[(findings["product"].eq("Khandan")) & findings["jalali_date"].eq("1404/01/14"), "action"].iloc[0], "keep")

    def test_invalid_jalali_date_is_preserved_for_review(self):
        frame = weekly_frame(
            ["1403/08/24", "1403/08/31", "1403/09/07"],
            [(100, 100), (100, 100), (100, 100)],
        )
        cleaned, findings = audit(frame)
        self.assertEqual(cleaned[DATE_COLUMN].tolist(), frame[DATE_COLUMN].tolist())
        invalid = findings[findings["jalali_date"].eq("1403/08/31")]
        self.assertEqual(set(invalid["action"]), {"manual_review"})


if __name__ == "__main__":
    unittest.main()
