"""Network-free tests for COCHILCO numeric vectors."""

from __future__ import annotations

import unittest

from commodity.copper.src.copper.collectors.cochilco import parse_vector


class VectorTests(unittest.TestCase):
    def test_spanish_numbers_and_missing_values(self) -> None:
        self.assertEqual(parse_vector("1.552,7  98,4  -"), [1552.7, 98.4, None])


if __name__ == "__main__":
    unittest.main()
