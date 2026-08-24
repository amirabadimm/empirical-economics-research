"""Network-free contracts for the integrated National Copper quarterly pipeline."""

from __future__ import annotations

import csv
import unittest
from pathlib import Path

from codal.national_copper.src.national_copper.collectors.financial_statements import (
    COMPANY,
    SYMBOL,
    is_parent_financial_filing,
    period_end,
)
from codal.national_copper.src.national_copper.processing.statement_parsing import (
    normalize_text,
    parse_number,
)
from codal.national_copper.src.national_copper.processing.build_quarterly_history import (
    AVAILABILITY_PATH,
    OUTPUT_PATH as QUARTERLY_OUTPUT_PATH,
)


class CodalMetadataTests(unittest.TestCase):
    def test_exact_parent_statement_scope(self) -> None:
        base = {
            "Symbol": SYMBOL,
            "CompanyName": COMPANY,
            "Title": "اطلاعات و صورت‌های مالی میاندوره‌ای دوره ۳ ماهه منتهی به ۱۴۰۵/۰۳/۳۱ (حسابرسی نشده)",
        }
        self.assertTrue(is_parent_financial_filing(base))
        self.assertTrue(
            is_parent_financial_filing(
                {**base, "Title": "صورت‌های مالی دوره ۶ ماهه منتهی به ۱۴۰۴/۰۶/۳۱"}
            )
        )
        self.assertTrue(
            is_parent_financial_filing(
                {**base, "Title": "صورت‌های مالی دوره ۹ ماهه منتهی به ۱۴۰۴/۰۹/۳۰"}
            )
        )
        self.assertFalse(is_parent_financial_filing({**base, "Title": base["Title"] + " تلفیقی"}))
        self.assertFalse(is_parent_financial_filing({**base, "CompanyName": "شرکت فرعی"}))

    def test_period_and_number_normalization(self) -> None:
        self.assertEqual(period_end("دوره ۳ ماهه منتهی به ۱۴۰۵/۰۳/۳۱"), "1405/03/31")
        self.assertEqual(parse_number("(۱,۲۳۴)"), -1234)
        self.assertEqual(normalize_text("هزينه‌های  عمومی"), "هزینه های عمومی")


class BuiltOutputTests(unittest.TestCase):
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
