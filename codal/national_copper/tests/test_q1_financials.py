"""Network-free contracts for the National Copper Q1 Codal pipeline."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path

from codal.national_copper.src.national_copper.collectors.financial_statements import (
    COMPANY,
    SYMBOL,
    is_q1_parent_filing,
    period_end,
)
from codal.national_copper.src.national_copper.processing.build_q1_history import (
    OUTPUT_PATH,
    normalize_text,
    parse_number,
)
from codal.national_copper.src.national_copper.processing.build_quarterly_history import (
    AVAILABILITY_PATH,
    OUTPUT_PATH as QUARTERLY_OUTPUT_PATH,
)


class CodalMetadataTests(unittest.TestCase):
    def test_exact_parent_q1_scope(self) -> None:
        base = {
            "Symbol": SYMBOL,
            "CompanyName": COMPANY,
            "Title": "اطلاعات و صورت‌های مالی میاندوره‌ای دوره ۳ ماهه منتهی به ۱۴۰۵/۰۳/۳۱ (حسابرسی نشده)",
        }
        self.assertTrue(is_q1_parent_filing(base))
        self.assertFalse(is_q1_parent_filing({**base, "Title": base["Title"] + " تلفیقی"}))
        self.assertFalse(is_q1_parent_filing({**base, "CompanyName": "شرکت فرعی"}))

    def test_period_and_number_normalization(self) -> None:
        self.assertEqual(period_end("دوره ۳ ماهه منتهی به ۱۴۰۵/۰۳/۳۱"), "1405/03/31")
        self.assertEqual(parse_number("(۱,۲۳۴)"), -1234)
        self.assertEqual(normalize_text("هزينه‌های  عمومی"), "هزینه های عمومی")


class BuiltOutputTests(unittest.TestCase):
    @unittest.skipUnless(OUTPUT_PATH.exists(), "local processed output is not present")
    def test_local_output_contract(self) -> None:
        with OUTPUT_PATH.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 20)
        self.assertEqual(rows[0]["period_end_jalali"], "1386/03/31")
        self.assertEqual(rows[-1]["period_end_jalali"], "1405/03/31")
        self.assertEqual({row["audit_status"] for row in rows}, {"حسابرسی نشده"})
        self.assertEqual(sum(row["wage_detail_available"] == "True" for row in rows), 7)
        self.assertEqual(
            sum(row["labor_data_status"].startswith("provisional_") for row in rows), 7
        )
        self.assertEqual(len({row["tracing_no"] for row in rows}), 20)

    @unittest.skipUnless(
        QUARTERLY_OUTPUT_PATH.exists() and AVAILABILITY_PATH.exists(),
        "local quarterly outputs are not present",
    )
    def test_local_quarterly_output_contract(self) -> None:
        with QUARTERLY_OUTPUT_PATH.open(encoding="utf-8-sig", newline="") as stream:
            rows = list(csv.DictReader(stream))
        with AVAILABILITY_PATH.open(encoding="utf-8-sig", newline="") as stream:
            availability = list(csv.DictReader(stream))
        self.assertEqual(len(rows), 75)
        self.assertEqual(len(availability), 80)
        self.assertEqual(sum(row["available"] == "False" for row in availability), 5)
        self.assertEqual(len({(row["fiscal_year_jalali"], row["quarter"]) for row in rows}), 75)
        self.assertEqual(sum(row["fiscal_year_jalali"] == "1386" for row in rows), 4)
        self.assertEqual(
            sum(row["labor_data_status"].startswith("provisional_") for row in rows), 22
        )
        self.assertTrue(
            all(row["current_statement_audit"] == "حسابرسی نشده" for row in rows if row["quarter"] != "4")
        )
        self.assertTrue(
            all(row["current_statement_audit"] == "حسابرسی شده" for row in rows if row["quarter"] == "4")
        )


if __name__ == "__main__":
    unittest.main()
