"""Regression tests for the generated Zinc benchmark and bubble datasets."""

from __future__ import annotations

import csv
import unittest
from decimal import Decimal
from pathlib import Path


PROJECT = Path(__file__).resolve().parents[1]
PROCESSED = PROJECT / "data" / "processed"


def rows(name: str, domain: str = "bubble") -> list[dict[str, str]]:
    path = PROCESSED / domain / name
    if not path.exists():
        raise unittest.SkipTest(f"generated dataset is unavailable: {path}")
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def d(value: str) -> Decimal:
    return Decimal(value)


class ZincBenchmarkTests(unittest.TestCase):
    def test_benchmark_is_unique_sorted_and_reconciles_grade_weights(self) -> None:
        data = rows("zinc_9798_cash_daily.csv", "physical")
        dates = [row["physical_trade_date_gregorian"] for row in data]
        self.assertEqual(dates, sorted(set(dates)))
        for row in data:
            self.assertLessEqual(set(row["grades"].split("|")), {"99.97", "99.98"})
            q97, q98, total = map(
                d, (row["grade_99_97_quantity"], row["grade_99_98_quantity"], row["total_quantity"])
            )
            self.assertEqual(q97 + q98, total)
            self.assertGreater(total, 0)
            numerator = Decimal(0)
            if q97:
                numerator += q97 * d(row["grade_99_97_weighted_price"])
            if q98:
                numerator += q98 * d(row["grade_99_98_weighted_price"])
            self.assertLess(
                abs(numerator / total - d(row["physical_weighted_price"])), Decimal("1e-18")
            )


class ZincBubbleTests(unittest.TestCase):
    def test_direct_bubbles_reconstruct_formula_and_have_nonnegative_source_ages(self) -> None:
        configurations = (
            (
                "physical_vs_intrinsic_bubble.csv",
                "physical_price_irr_per_kg",
                "physical_vs_intrinsic_bubble_pct",
            ),
            (
                "certificate_vs_intrinsic_bubble.csv",
                "certificate_price_irr_per_kg",
                "certificate_vs_intrinsic_bubble_pct",
            ),
        )
        for filename, price_column, bubble_column in configurations:
            for row in rows(filename):
                expected = (d(row[price_column]) / d(row["intrinsic_price_irr_per_kg"]) - 1) * 100
                self.assertLess(abs(expected - d(row[bubble_column])), Decimal("1e-18"))
                self.assertGreaterEqual(int(row["lme_age_days"]), 0)
                self.assertGreaterEqual(int(row["usd_age_days"]), 0)

    def test_primary_bubble_has_anchors_no_extrapolation_and_reconstructs_anchors(self) -> None:
        data = rows("zinc_certificate_bubble.csv")
        observed = [row for row in data if row["physical_ratio_method"] == "observed"]
        interpolated = [
            row for row in data if row["physical_ratio_method"] == "linear_interpolation"
        ]
        self.assertGreater(len(observed), 0)
        self.assertEqual(len(data), len(observed) + len(interpolated))
        self.assertEqual(data[0]["date"], observed[0]["date"])
        self.assertEqual(data[-1]["date"], observed[-1]["date"])
        for row in observed:
            self.assertEqual(row["ratio_left_anchor_date"], row["date"])
            self.assertEqual(row["ratio_right_anchor_date"], row["date"])
            self.assertLess(
                abs(
                    d(row["observed_physical_price_irr_per_kg"])
                    - d(row["estimated_physical_price_irr_per_kg"])
                ),
                Decimal("1e-18"),
            )
        for row in data:
            expected = (
                d(row["certificate_price_irr_per_kg"])
                / d(row["estimated_physical_price_irr_per_kg"])
                - 1
            ) * 100
            self.assertLess(abs(expected - d(row["certificate_bubble_pct"])), Decimal("1e-18"))

    def test_regression_has_one_selected_model_and_all_certificate_dates(self) -> None:
        metrics = rows("intrinsic_regression_metrics.csv")
        regression = rows("intrinsic_regression.csv")
        direct = rows("certificate_vs_intrinsic_bubble.csv")
        self.assertEqual(sum(row["selected"] == "1" for row in metrics), 1)
        self.assertEqual(len(regression), len(direct))
        primary = rows("zinc_certificate_bubble.csv")
        observed_count = sum(row["physical_ratio_method"] == "observed" for row in primary)
        self.assertEqual(
            sum(row["is_actual_physical_observation"] == "1" for row in regression),
            observed_count,
        )


if __name__ == "__main__":
    unittest.main()
