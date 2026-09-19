"""Collector contract checks that do not require network access."""

import csv
import tempfile
import unittest
from datetime import date
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from pista.collectors.certificate import (  # noqa: E402
    CONFIG, RAW_COLUMNS, chunks, read_existing, validate_record, write_atomic,
)


class CertificateCollectorTests(unittest.TestCase):
    def test_project_identity_and_date_chunks(self):
        self.assertEqual(CONFIG.codes, {"PistaCL"})
        self.assertEqual(CONFIG.first_query_date, date(2026, 8, 25))
        periods = list(chunks(date(2026, 8, 25), date(2027, 3, 1)))
        self.assertEqual(periods[0], (date(2026, 8, 25), date(2027, 2, 20)))
        self.assertEqual(periods[1][0], date(2027, 2, 21))

    def test_rejects_wrong_contract(self):
        record = {field: 0 for field in RAW_COLUMNS[:-2]}
        record.update(CommodityID=11, ContractCode="Other", DT="2026-08-25T00:00:00")
        with self.assertRaisesRegex(ValueError, "Unexpected contract code"):
            validate_record(record, CONFIG)

    def test_atomic_csv_round_trip(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parents[1]) as directory:
            path = Path(directory) / "certificate.csv"
            row = {field: "" for field in RAW_COLUMNS}
            row["DT"] = "2026-08-25T00:00:00"
            write_atomic(path, {"2026-08-25": row})
            self.assertEqual(read_existing(path)["2026-08-25"]["DT"], row["DT"])
            with path.open(encoding="utf-8-sig", newline="") as handle:
                self.assertEqual(next(csv.reader(handle)), RAW_COLUMNS)


if __name__ == "__main__":
    unittest.main()
